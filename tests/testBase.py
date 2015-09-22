from dnsyo import lookup
import os

class testBase(object):
  """
  Base for other test classes
  """

  resolversList = "https://www.codesam.co.uk/files/dnsyo/list/resolver-list.yml"
  listLocal = "~/.dnsyo-resolvers-list.yaml"

  def createLookup(self,**lookupParams):
    """
    Create a lookup class
    """

    baseLookupParams = {
      'listLocation': self.resolversList,
      'listLocal': self.listLocal
    }
    baseLookupParams.update(lookupParams)
    return lookup(**baseLookupParams)

  def setup(self, **lookupParams):
    """
    Ensure there isn't a local list and create a lookup object
    """

    if os.path.isfile(self.listLocal):
      os.remove(self.listLocal)

    self.lookup = self.createLookup(**lookupParams)
    self.lookup.updateList()
