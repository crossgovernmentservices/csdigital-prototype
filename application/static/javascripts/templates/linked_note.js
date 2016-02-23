function templateObjectivesLinkedNote(context) {
    var __result = "";
    var __tmp;
    var __runtime = jinjaToJS.runtime;
    var __filters = jinjaToJS.filters;
    __result += "<li class=\"linked-item\">\n  <a href=\"";__result += "" + __runtime.escape((__tmp = (context.note.url)) == null ? "" : __tmp);__result += "\">";__result += "" + __runtime.escape((__tmp = (__filters.truncate(context.note.entry.title,40))) == null ? "" : __tmp);__result += "</a>\n  <span class=\"remove-link\"><a href=\"";__result += "" + __runtime.escape((__tmp = (context.note.promote_url)) == null ? "" : __tmp);__result += "\" title=\"add as evidence\">upgrade to evidence</a></span>\n</li>";
    return __result;
}