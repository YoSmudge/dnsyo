import testBase
from nose.tools import *
from dnsyo import lookup
import os
import time

class testList(testBase.testBase):
  """
  Test downloading the list file, parsing and filtering
  """

  def getListMod(self):
    """
    Get the last modified time of the list
    """

    return os.path.getmtime(
      os.path.expanduser(self.listLocal)
    )

  def test_download(self):
    """
    Download the list
    """

    assert_true(os.path.isfile(os.path.expanduser(self.listLocal)))

  def test_parse(self):
    """
    Download and parse the list
    """

    servers = self.lookup.prepareList()
    assert_greater(len(servers), 0)

  def test_filtering(self):
    """
    Filter the list
    """

    l = self.createLookup(
      maxServers=50
    )
    assert_equal(len(l.prepareList()), 50)

    l = self.createLookup(
      country="US"
    )
    assert_true(
      all([True for s in l.prepareList() if s['country'] == "US"])
    )

  def test_update(self):
    """
    Test expiring the list
    """

    listExpires = self.lookup.updateListEvery
    expiredTime = time.time() - listExpires - 60
    os.utime(
      os.path.expanduser(self.listLocal),
      (expiredTime, expiredTime)
    )

    oldTime = self.getListMod()

    assert_less(oldTime, time.time() - listExpires)
    self.lookup.updateList()

    newTime = self.getListMod()

    assert_greater(newTime, oldTime)
    assert_greater(newTime, expiredTime)

  def test_server_error(self):
    """
    500 error when downloading list

    Shouldn't delete old list when one is present
    Should raise exception without
    """

    oldMod = self.getListMod()
    l = self.createLookup(listLocation="https://httpbin.org/status/500")
    l.updateList()
    newMod = self.getListMod()
    assert_equal(oldMod, newMod)
    assert_true(os.path.isfile(os.path.expanduser(self.listLocal)))

    os.remove(os.path.expanduser(self.listLocal))
    assert_raises(EnvironmentError, l.updateList)
