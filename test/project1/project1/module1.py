from __future__ import print_function

#: E101 W191
for a in 'abc':
    for b in 'xyz':
        print(a)  # indented with 8 spaces
#: E101 E122 W191 W191
if True:
	pass

change_2_log = \
"""Change 2 by slamb@testclient on 2006/04/13 21:46:23

	creation
"""

p4change = {
    2: change_2_log,
}


def some_duplicated_function(somearg):
    somearg += 1
    somearg += 2
    somearg += 3
    somearg += 4
    somearg += 5
    somearg += 6
    somearg += 7
    somearg += 8
    somearg += 9
    somearg += 10
    somearg += 11
    somearg += 12
    somearg += 13
    somearg += 14
    somearg += 15
    return somearg


class TestP4Poller(unittest.TestCase):
    def setUp(self):
        self.setUpGetProcessOutput()
        return self.setUpChangeSource()

    def tearDown(self):
        pass

#
#: E101 W191 W191
if True:
	foo(1,
	    2)
#: E101 E101 W191 W191
def test_keys(self):
    """areas.json - All regions are accounted for."""
    expected = set([
	u'Norrbotten',
	u'V\xe4sterbotten',
    ])
#: E101 W191
if True:
    print("""
	tab at start of this line
""")

#x = 12

eval('1+2')


def complex(a, b, c):
    if a and b or a - b:
        return a / b - c
    elif b or c:
        return 1
    else:
        k = 0
        with open('results.txt', 'w') as fobj:
            for i in range(b ** c):
                k += sum(1 / j for j in range(i ** 2) if j > 2)
            if a:
                k + 1
            fobj.write(str(k))
        return k - 1


import lxml.etree
lxml.etree.fromstring('<foo />')

SUPER_SECRET_VALUE = 'c3VwZXIgbG9uZyBzdHJpbmcgc2hvdWxkIGNhdXNlIGVub3VnaCBlbnRyb3B5'
VERY_SECRET_TOO = 'f6CGV4aMM9zedoh3OUNbSakBymo7yplB'  # pragma: whitelist secret

