#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import itertools

import pytest

from ocean.tests import util

from uiutil import *

@pytest.fixture(scope='module')
def wcag(driver, url):
    """
    Set up a single session for these tests.
    """

    b = driver
    b.set_window_size(1200, 800)
    b.get(url)

    b.select_param('variable', 'Anomalies')
    b.select_param('plottype', 'Surface Map')
    b.select_param('period', '3 monthly')
    b.select_param('year', '2012')
    b.select_param('month', 'Jan 12 - Mar 12')
    b.select_param('dataset', 'ERSST')

    b.submit()
    b.wait(output('ERA'))

    return b

@pytest.mark.wcagF17
@pytest.mark.wcagF62
@pytest.mark.wcagF77
def test_unique_ids(wcag):
    """
    All ids in the document should be unique.
    """

    elems = wcag.find_elements_by_jquery('[id]')
    ids = map(lambda e: e.get_attribute('id'), elems)

    assert len(elems) >= 1 # sanity check
    assert util.unique(ids)

@pytest.mark.wcagF17
def test_unique_accesskeys(wcag):
    """
    All accesskeys in the document should be unique.
    """

    elems = wcag.find_elements_by_jquery('[accesskey]')
    accesskeys = itertools.chain.from_iterable(
        map(lambda e: e.get_attribute('accesskey').split(' '),
            elems))

    assert util.unique(accesskeys)

@pytest.mark.xfail
@pytest.mark.wcagF17
def test_labels_have_for(wcag):
    """
    All label elements must have a for attribute, which must point to
    a valid id.
    """

    failed = False
    elems = wcag.find_elements_by_jquery('label')

    for elem in elems:
        try:
            for_ = elem.get_attribute('for')

            assert for_ is not None, "<label> element must have @for attribute"

            control = wcag.find_element_by_id(for_)

            assert control is not None
        except AssertionError as e:
            print "%s (%s): %s" % (elem, elem.text, e)
            failed = True

    assert not failed

@pytest.mark.xfail
@pytest.mark.wcagF68
def test_controls_have_label_or_title(wcag):
    """
    Most controls require either a specific label, or a title attribute.

    http://www.w3.org/TR/2012/NOTE-WCAG20-TECHS-20120103/F68
    """

    controls = [
        'input[type="text"]',
        'input[type="checkbox"]',
        'input[type="radio"]',
        'input[type="file"]',
        'input[type="password"]',
        'textarea',
        'select',
    ]

    failed = False
    elems = map(lambda c: wcag.find_elements_by_jquery(c),
                                controls)
    elems = list(itertools.chain.from_iterable(elems))
    assert len(elems) >= 1 # sanity check

    # FIXME: should fail on OpenLayers
    for elem in elems:
        try:
            id = elem.get_attribute('id')

            if len(id) > 0:
                # find any labels pointing to this element
                nlabels = \
                    len(wcag.find_elements_by_jquery('label[for="%s"]' % id))

                assert nlabels < 2, "Multiple labels point to item"
                if nlabels == 1:
                    # don't need a title if we have a label
                    continue

            # find a title
            title = elem.get_attribute('title')
            assert len(title) > 0, "No <label>, must have @title attribute"
        except AssertionError as e:
            print "%s: %s" % (elem, e)
            failed = True

    assert not failed

@pytest.mark.wcagF89
def test_linked_images_have_alt_text(wcag):

    failed = False
    elems = wcag.find_elements_by_xpath('//a[img]')

    assert len(elems) > 0 # sanity check

    for elem in elems:
        text = elem.text.strip()
        img = elem.find_element_by_tag_name('img')

        try:
            assert len(text) > 0 or \
                   len(elem.get_attribute('title')) > 0 or \
                   len(img.get_attribute('alt')) > 0, \
                   "a/img must have text, @title or @alt"
        except AssertionError as e:
            print "%s: %s" % (elem, e)
            failed = True

    assert not failed

@pytest.mark.xfail
@pytest.mark.wcagF38
@pytest.mark.wcagF65
def test_img_have_alt_attributes(wcag):

    elements = ['img', 'area', 'input[type="image"]']
    query = ':not([alt])'

    elems = map(lambda c: wcag.find_elements_by_jquery(c),
                map(lambda e: e + query, elements))
    elems = list(itertools.chain.from_iterable(elems))

    for elem in elems:
        print "%s: Must have @alt attribute" % (elem)
        failed = True

    assert not failed
