function templateObjectivesComment(context) {
    var __result = "";
    var __tmp;
    var __runtime = jinjaToJS.runtime;
    var __filters = jinjaToJS.filters;
    __result += "<li>\n  <div class=\"comment\">\n    <dl class=\"comment__metadata definition-inline\">\n      <dt class=\"visuallyhidden\">From</dt><dd>";__result += "" + __runtime.escape((__tmp = (context.comment.author)) == null ? "" : __tmp);__result += "</dd>\n      <dt>Date</dt><dd>";__result += "" + __runtime.escape((__tmp = (context.comment.created)) == null ? "" : __tmp);__result += "</dd>\n    </dl>\n    <div class=\"comment__content\">\n      ";__result += "" + __runtime.escape((__tmp = (context.comment.content)) == null ? "" : __tmp);__result += "\n    </div>\n  </div>\n</li>";
    return __result;
}