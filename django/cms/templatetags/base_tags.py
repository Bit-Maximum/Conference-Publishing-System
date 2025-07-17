from django import template

from wagtail.models import Site, Page

from cms.models import Footer, InstructionPage


register = template.Library()


@register.inclusion_tag('tags/footer.html', takes_context=True)
def footer_tag(context):
    return {'request': context['request'], 'footer': Footer.objects.first()}


@register.simple_tag(takes_context=True)
def get_site_root(context):
    return Site.find_for_request(context["request"]).root_page


@register.simple_tag(takes_context=True)
def get_instruction_root(context):
    parent = Site.find_for_request(context["request"]).root_page
    menuitems = Page.objects.type(InstructionPage)
    print(menuitems)
    for menuitem in menuitems:
        print(type(menuitem))
        print(isinstance(menuitem, InstructionPage))
        if menuitem.content_type == InstructionPage:
            print("InstructionPage --- ewretgefd")
            return menuitem
    return


def has_menu_children(page):
    return page.get_children().live().in_menu().exists()


@register.inclusion_tag("tags/instructions_menu_children.html", takes_context=True)
def instruction_menu(context):
    menuitems = InstructionPage.objects.all()
    has_staff_only = False
    for menuitem in menuitems:
        if menuitem.staff_only:
            has_staff_only = True
            break
    return {
        "menuitems": menuitems,
        "has_staff_only": has_staff_only,
        "request": context["request"],
    }


@register.inclusion_tag("tags/top_menu_children.html", takes_context=True)
def top_menu_children(context, parent):
    menuitems_children = parent.get_children()
    menuitems_children = menuitems_children.live().in_menu()
    print(menuitems_children)
    for menuitem in menuitems_children:
        menuitem.children = menuitem.get_children().live().in_menu()
        print(menuitem)
    print(menuitems_children)
    return {
        "parent": parent,
        "menuitems_children": menuitems_children,
        "request": context["request"],
    }
