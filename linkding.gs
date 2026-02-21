/**
 * Linkding Bookmark Reminder — Google Apps Script
 *
 * Fetches bookmarks from a Linkding instance and emails them as a daily
 * reminder using Gmail.
 *
 * SETUP
 * ─────
 * 1. Open https://script.google.com/ and create a new project.
 * 2. Paste this entire file into Code.gs.
 * 3. Run the  setup()  function once — it will prompt for your config
 *    and create a daily trigger.
 * 4. Authorise the script when prompted.
 *
 * You can also set properties manually under
 *   Project Settings → Script Properties:
 *
 *   LINKDING_URL        (required)  e.g. http://192.168.50.5:9090
 *   LINKDING_PUBLIC_URL  (optional) e.g. https://links.example.com
 *   LINKDING_TOKEN       (required)  API token
 *   LINKDING_TAGS        (optional)  comma-separated, default "2do"
 *   EMAIL_RECIPIENT      (required)  destination email address
 */

// ─────────────────────────────────────────────
//  Entry point — called by the daily trigger
// ─────────────────────────────────────────────

function main() {
  var props = PropertiesService.getScriptProperties().getProperties();

  var linkdingUrl   = props["LINKDING_URL"];
  var publicUrl     = props["LINKDING_PUBLIC_URL"] || linkdingUrl;
  var token         = props["LINKDING_TOKEN"];
  var tagsRaw       = props["LINKDING_TAGS"] || "2do";
  var recipient     = props["EMAIL_RECIPIENT"];

  // Validate
  if (!linkdingUrl || !token || !recipient) {
    throw new Error(
      "Missing required Script Properties. " +
      "Please set LINKDING_URL, LINKDING_TOKEN, and EMAIL_RECIPIENT."
    );
  }

  var tags = parseTags(tagsRaw);

  Logger.log("Fetching bookmarks for tags: " + tags.map(function(t){ return "#" + t; }).join(", "));

  var bookmarks = getBookmarksByTags(linkdingUrl, token, tags);

  Logger.log("Found " + bookmarks.length + " bookmarks");

  var subject  = "Bookmarks: " + tags.map(function(t){ return "#" + t; }).join(", ");
  var htmlBody = buildHtmlBody(bookmarks, tags, publicUrl);
  var textBody = buildPlainTextBody(bookmarks, tags, publicUrl);

  MailApp.sendEmail({
    to:       recipient,
    subject:  subject,
    body:     textBody,
    htmlBody: htmlBody
  });

  Logger.log("Email sent successfully!");
}

// ─────────────────────────────────────────────
//  Linkding API
// ─────────────────────────────────────────────

/**
 * Fetch bookmarks matching any of the given tags, de-duplicated by URL.
 */
function getBookmarksByTags(baseUrl, token, tags) {
  var allBookmarks = [];

  for (var i = 0; i < tags.length; i++) {
    var tag = tags[i];
    try {
      var results = fetchBookmarksForTag(baseUrl, token, tag);
      for (var j = 0; j < results.length; j++) {
        results[j]._query_tag = tag;
        allBookmarks.push(results[j]);
      }
    } catch (e) {
      Logger.log("Error fetching bookmarks for tag '" + tag + "': " + e);
    }
  }

  // De-duplicate by URL
  var seen = {};
  var unique = [];
  for (var k = 0; k < allBookmarks.length; k++) {
    var url = allBookmarks[k].url || "";
    if (url && !seen[url]) {
      seen[url] = true;
      unique.push(allBookmarks[k]);
    }
  }

  return unique;
}

/**
 * Fetch all pages of bookmarks for a single tag from the Linkding API.
 */
function fetchBookmarksForTag(baseUrl, token, tag) {
  var results = [];
  var url = baseUrl.replace(/\/+$/, "") + "/api/bookmarks/?q=" + encodeURIComponent("#" + tag) + "&limit=100";

  while (url) {
    var response = UrlFetchApp.fetch(url, {
      method: "get",
      headers: { "Authorization": "Token " + token },
      muteHttpExceptions: true
    });

    if (response.getResponseCode() !== 200) {
      throw new Error("HTTP " + response.getResponseCode() + ": " + response.getContentText());
    }

    var data = JSON.parse(response.getContentText());
    var items = data.results || [];
    results = results.concat(items);

    // Follow pagination
    url = data.next || null;
  }

  return results;
}

// ─────────────────────────────────────────────
//  Email body builders
// ─────────────────────────────────────────────

function buildHtmlBody(bookmarks, tags, publicUrl) {
  var tagList = tags.map(function(t){ return "#" + t; }).join(", ");

  // Header
  var headerHtml = "";
  if (publicUrl) {
    headerHtml =
      '<pre style="margin: 0; padding: 10px 0; border-bottom: 1px solid #ccc; font-family: monospace; font-size: 12px; color: #666;">\n' +
      "BOOKMARK REMINDER\n" +
      "Reminding you of the latest links at " + publicUrl + "\n" +
      "</pre>";
  }

  if (bookmarks.length === 0) {
    return "<html><body style=\"font-family: monospace; margin: 0; padding: 20px; background: #fff; color: #000; font-size: 12px; line-height: 1.4;\">" +
      headerHtml +
      '<pre style="margin: 20px 0;">\nNo bookmarks found for tags: ' + tagList + "\n</pre>" +
      "</body></html>";
  }

  var parts = [
    "<html>",
    "<body style='font-family: monospace; margin: 0; padding: 20px; background: #fff; color: #000; font-size: 12px; line-height: 1.4;'>",
    headerHtml,
    "<pre style='margin: 20px 0;'>" + bookmarks.length + " bookmarks for " + tagList + "</pre>"
  ];

  for (var i = 0; i < bookmarks.length; i++) {
    var bm = bookmarks[i];
    var title     = bm.title || "(no title)";
    var bmUrl     = (bm.url || "").split("#")[0];
    var bmTags    = bm.tag_names || [];
    var queryTag  = bm._query_tag || "";

    var tagText = "";
    if (bmTags.length > 0) {
      tagText = " | " + bmTags.join(", ");
    }

    parts.push("<pre style='margin: 5px 0; padding: 2px 0;'>");
    parts.push("<a href='" + bmUrl + "' style='color: #0066cc; text-decoration: none;'>" + escapeHtml(title) + "</a> | #" + escapeHtml(queryTag) + escapeHtml(tagText));
    parts.push(escapeHtml(bmUrl));
    parts.push("</pre>");
  }

  parts.push("</body>");
  parts.push("</html>");

  return parts.join("\n");
}

function buildPlainTextBody(bookmarks, tags, publicUrl) {
  var tagList = tags.map(function(t){ return "#" + t; }).join(", ");

  var lines = [];

  if (publicUrl) {
    lines.push("BOOKMARK REMINDER");
    lines.push("Reminding you of the latest links at " + publicUrl);
    lines.push("--------------------------------------------------");
    lines.push("");
  }

  if (bookmarks.length === 0) {
    lines.push("No bookmarks found for tags: " + tagList);
    return lines.join("\n");
  }

  lines.push(bookmarks.length + " bookmarks for " + tagList);
  lines.push("");

  for (var i = 0; i < bookmarks.length; i++) {
    var bm = bookmarks[i];
    var title     = bm.title || "(no title)";
    var bmUrl     = (bm.url || "").split("#")[0];
    var bmTags    = bm.tag_names || [];
    var queryTag  = bm._query_tag || "";

    var tagText = "";
    if (bmTags.length > 0) {
      tagText = " | " + bmTags.join(", ");
    }

    lines.push(title + " | #" + queryTag + tagText);
    lines.push(bmUrl);
  }

  return lines.join("\n");
}

// ─────────────────────────────────────────────
//  Helpers
// ─────────────────────────────────────────────

function parseTags(raw) {
  if (!raw) return ["2do"];
  var tags = raw.split(",").map(function(t){ return t.trim(); }).filter(function(t){ return t.length > 0; });
  return tags.length > 0 ? tags : ["2do"];
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ─────────────────────────────────────────────
//  One-time setup — run this manually once
// ─────────────────────────────────────────────

/**
 * One-time setup: creates the daily trigger.
 * Run this function once from the Apps Script editor.
 *
 * Before running, add these Script Properties manually:
 *   Project Settings (⚙️) → Script Properties → Add Property
 *
 *   LINKDING_URL         (required)  e.g. http://192.168.50.5:9090
 *   LINKDING_PUBLIC_URL  (optional)  e.g. https://links.example.com
 *   LINKDING_TOKEN       (required)  API token
 *   LINKDING_TAGS        (optional)  comma-separated, default "2do"
 *   EMAIL_RECIPIENT      (required)  destination email address
 */
function setup() {
  // Remove existing triggers for main() to avoid duplicates
  var triggers = ScriptApp.getProjectTriggers();
  for (var t = 0; t < triggers.length; t++) {
    if (triggers[t].getHandlerFunction() === "main") {
      ScriptApp.deleteTrigger(triggers[t]);
    }
  }

  ScriptApp.newTrigger("main")
    .timeBased()
    .everyDays(1)
    .atHour(8)          // 8 AM in your script's timezone
    .create();

  Logger.log("Daily trigger created — main() will run every day at ~8 AM.");
  Logger.log("Make sure you have set the required Script Properties before the first run.");
}
