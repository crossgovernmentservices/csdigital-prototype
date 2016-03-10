function templateLinkedNote(context) {
    var __result = "";
    var __tmp;
    var __runtime = jinjaToJS.runtime;
    var __filters = jinjaToJS.filters;
    __result += "<a href=\"";__result += "" + __runtime.escape((__tmp = (context.note.url)) == null ? "" : __tmp);__result += "\">";__result += "" + __runtime.escape((__tmp = (__filters.truncate(context.note.entry.title,40))) == null ? "" : __tmp);__result += "</a>";
    return __result;
}