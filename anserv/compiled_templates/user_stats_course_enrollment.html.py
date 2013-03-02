# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1360879167.896423
_enable_loop = True
_template_filename = 'templates/user_stats_course_enrollment.html'
_template_uri = 'user_stats_course_enrollment.html'
_source_encoding = 'utf-8'
_exports = []


# SOURCE LINE 2

import simplejson as json


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        courses_by_term = context.get('courses_by_term', UNDEFINED)
        unis = context.get('unis', UNDEFINED)
        terms_by_course = context.get('terms_by_course', UNDEFINED)
        terms = context.get('terms', UNDEFINED)
        courses = context.get('courses', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'<script>\n    ')
        # SOURCE LINE 4
        __M_writer(u'\n    course_enrollment_unis = ')
        # SOURCE LINE 5
        __M_writer(unicode(json.dumps(unis)))
        __M_writer(u';\n    course_enrollment_courses = ')
        # SOURCE LINE 6
        __M_writer(unicode(json.dumps(courses)))
        __M_writer(u';\n    course_enrollment_terms = ')
        # SOURCE LINE 7
        __M_writer(unicode(json.dumps(terms)))
        __M_writer(u';\n    course_enrollment_terms_by_course = ')
        # SOURCE LINE 8
        __M_writer(unicode(json.dumps(terms_by_course)))
        __M_writer(u';\n    course_enrollment_courses_by_term = ')
        # SOURCE LINE 9
        __M_writer(unicode(json.dumps(courses_by_term)))
        __M_writer(u';\n    \n    var sel_uni, sel_course, sel_term;   \n         \n    function load_course_enrol_stats_by_course(uni, course)\n    {\n        var j=1, d1 = [], ticks = [];\n        for (var term in course_enrollment_terms_by_course[uni][course])\n        {\n            d1.push([j, parseInt(course_enrollment_terms_by_course[uni][course][term])]);\n            ticks.push([j, term]);\n            j++;\n        }       \n    \n        $(\'#graph\').css(\'height\', \'500px\');\n        $.plot($("#graph"), \n            [{\n                data: d1,\n                bars: { \n                    show: true,\n                    align: "center"\n                }\n            }],\n            {\n                xaxis: {\n                    ticks: ticks\n                }\n            });\n    }\n    function load_course_enrol_stats_by_term(uni, term)\n    {       \n        var j=1, d1 = [], ticks = [];\n        for (var course in course_enrollment_courses_by_term[uni][term])\n        {\n            d1.push([j, parseInt(course_enrollment_courses_by_term[uni][term][course])]);\n            ticks.push([j, course]);\n            j++;\n        }                     \n    \n        $(\'#graph\').css(\'height\', \'500px\');\n        $.plot($("#graph"), \n            [{\n                data: d1,                \n                bars: { \n                    show: true,\n                    align: "center"\n                }\n            }],\n            {\n                xaxis: {\n                    ticks: ticks\n                },\n            });\n    }\n    function load_course_enrol_stats_by_term_all(uni)\n    { \n        var i,j; var d = []; var ticks = [];\n        for (i=0; i<course_enrollment_courses[uni].length;i++)\n        {\n            course = course_enrollment_courses[uni][i];\n            var d1 = [];\n            for (j=0;j<course_enrollment_terms[uni].length;j++)\n            {\n                d1.push([j, course_enrollment_terms_by_course[uni][course][course_enrollment_terms[uni][j]]]);\n            }\n            \n            d.push({\n                label: course,\n                data: d1,\n                bars: { \n                    order: i+1,\n                    barWidth: 1.0/course_enrollment_courses[uni].length,\n                    show: true,\n                    align: "center"\n                }\n            });\n        }\n        //alert(JSON.stringify(d));\n        for (i=0;i<course_enrollment_terms[uni].length;i++)\n            ticks.push([i, course_enrollment_terms[uni][i]]);\n    \n        $(\'#graph\').css(\'height\', \'500px\');\n        $.plot($("#graph"), \n            d,\n            {\n                xaxis: {\n                    ticks: ticks\n                },\n                //grid: {hoverable: true},\n                multiplebars:true,\n            });\n    }\n    function load_course_enrol_stats_by_course_all(uni)\n    {\n        var i,j; var d = []; var ticks = [];\n        for (i=0; i<course_enrollment_terms[uni].length;i++)\n        {\n            term = course_enrollment_terms[uni][i];\n            var d1 = [];\n            for (j=0;j<course_enrollment_courses[uni].length;j++)\n            {\n                d1.push([j, course_enrollment_courses_by_term[uni][term][course_enrollment_courses[uni][j]]]);\n            }\n            \n            d.push({\n                label: term,\n                data: d1,\n                bars: { \n                    order: i+1,\n                    show: true,\n                    barWidth: 1.0/course_enrollment_terms[uni].length,\n                    align: "center"\n                },\n                legend: {\n                    show: true,\n                    position: "ne",\n                    noColumns: course_enrollment_terms[uni].length\n                }       \n\n            });\n        }\n        //alert(JSON.stringify(d));\n        for (i=0;i<course_enrollment_courses[uni].length;i++)\n            ticks.push([i, course_enrollment_courses[uni][i]]);\n    \n        $(\'#graph\').css(\'height\', \'500px\');\n        $.plot($("#graph"), \n            d,\n            {\n                xaxis: {\n                    ticks: ticks\n                },\n                //grid: {hoverable: true},\n                multiplebars:true\n            });\n    }\n    function load_course_from_univ(uni)\n    {       \n        sel_uni = uni;\n        \n        $(\'#cat-nav-bycourse\').empty().append(\n            $(\'<li>\').append(\n                $(\'<a href="#" onclick="load_course_enrol_stats_by_course_all(sel_uni);">All</a>\')\n            )\n        ).append(\n            $(\'<li class="divider">\')\n        );\n        $(\'#cat-nav-byterm\').empty().append(\n            $(\'<li>\').append(\n                $(\'<a href="#" onclick="load_course_enrol_stats_by_term_all(sel_uni);">All</a>\')\n            )\n        ).append(\n            $(\'<li class="divider">\')\n        );\n                \n        \n        for (i=0;i<course_enrollment_courses[uni].length;i++)\n            $(\'#cat-nav-bycourse\').append(\n                $(\'<li>\').append(\n                    $(\'<a href="#" onclick="load_course_enrol_stats_by_course(\\\'\' + uni + \'\\\', \\\'\' + course_enrollment_courses[uni][i] + \'\\\');">\' + course_enrollment_courses[uni][i] + \'</a>\')\n                )\n            );\n        \n        for (i=0;i<course_enrollment_terms[uni].length;i++)\n            $(\'#cat-nav-byterm\').append(\n                $(\'<li>\').append(\n                    $(\'<a href="#" onclick="load_course_enrol_stats_by_term(\\\'\' + uni + \'\\\', \\\'\' + course_enrollment_terms[uni][i] + \'\\\');">\' + course_enrollment_terms[uni][i] + \'</a>\')\n                )\n            );  \n            \n        load_course_enrol_stats_by_course_all(uni);      \n    }\n</script>\n<ul id="uni-nav" class="nav nav-tabs">\n')
        # SOURCE LINE 183
        for uni in unis:
            # SOURCE LINE 184
            __M_writer(u'        <li class="uni-nav-li"><a href="#" onclick="$(\'.uni-nav-li\').attr(\'class\', \'uni-nav-li\'); $(this).parent().attr(\'class\', \'active uni-nav-li\'); load_course_from_univ(\'')
            __M_writer(unicode(uni))
            __M_writer(u'\');">')
            __M_writer(unicode(uni))
            __M_writer(u'</a></li>\n')
        # SOURCE LINE 186
        __M_writer(u'</ul>\n    \n<ul id="cat-nav" class="nav nav-pills">\n    <li class="dropdown">\n        <a class="dropdown-toggle" data-toggle="dropdown" href="#">By Course <b class="caret"></b></a>\n        <ul id="cat-nav-bycourse" class="dropdown-menu"></ul>\n    </li>\n    <li class="dropdown">\n        <a class="dropdown-toggle" data-toggle="dropdown" href="#">By Term<b class="caret"></b></a>\n        <ul id="cat-nav-byterm" class="dropdown-menu"></ul>\n    </li>\n</ul>\n\n<script>$(".uni-nav-li").first().children().first().click();</script>\n\n<div id="graph"></div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


