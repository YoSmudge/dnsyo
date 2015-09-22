import testBase
from nose.tools import *
import logging

class testLookupValidation(testBase.testBase):
  """
  Test lookup validates parameters properly
  """

  defaultTestDomain = 'www.codesam.co.uk'

  def doLookup(self, query):
    """
    Single lookup test case
    """

    servers = self.lookup.prepareList()
    self.lookup.query(
      query[1],
      recordType=query[0],
      progress=False
    )

    logging.debug("Returned results are: {0}".format(
      ", ".join([str(r['results']) for r in self.lookup.results])
    ))

    assert_true(
      any([
        True for r in self.lookup.results
        if query[2] in r['results']
      ])
    )

    assert_equal(len(self.lookup.results), len(servers))

  def test_lookups(self):
    """
    Run various lookup test casses
    """

    tests = [
      ("A", self.defaultTestDomain, "188.165.232.223"),
      ("CNAME", self.defaultTestDomain, "codesam.co.uk."),
      ("MX", self.defaultTestDomain, "1 codesam-co-uk.mail.protection.outlook.com."),
      ("NS", self.defaultTestDomain, "ns-1815.awsdns-34.co.uk.")
    ]

    for t in tests:
      yield self.doLookup, t

  def test_basicLookup(self):
    """
    Run a lookup and check it returns results
    """

    self.lookup.query(
      self.defaultTestDomain,
      recordType="A",
      progress=False
    )

    assert_greater(len(self.lookup.results), 0)
    assert_greater(len(self.lookup.resultsColated), 0)
