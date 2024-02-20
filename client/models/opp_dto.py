
import pprint
import re

import six

class OppDto(object):
    """
    Attributes:
      types (dict): The key is attribute name
                    and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    
    types = {'title': 'str',
             'agency': 'str',
             'posted_date': 'str',
             'type': 'str',
             'set_aside': 'str',
             'due_date': 'str',
             'naics': 'str',
             'url': 'str'}

    attribute_map = {'title': 'title',
                     'agency': 'fullParentPathName',
                     'posted_date': 'postedDate',
                     'type': 'type',
                     'set_aside': 'typeOfSetAsideDescription',
                     'due_date': 'responseDeadLine',
                     'naics': 'naicsCode',
                     'url': 'uiLink'}

    def __init__(self, title=None, agency=None, posted_date=None,
                 type=None, set_aside=None, due_date=None,
                 naics=None, url=None):
        
        self._title = None
        self._agency = None
        self._posted_date = None
        self._type = None
        self._set_aside = None
        self._due_date = None
        self._naics = None
        self._url = None
        self.discriminator = None

        if title is not None:
            self.title = title
        if agency is not None:
            self.agency = agency
        if posted_date is not None:
            self.posted_date = posted_date
        if type is not None:
            self.type = type
        if set_aside is not None:
            self.set_aside = set_aside
        if due_date is not None:
            self.due_date = due_date
        if naics is not None:
            self.naics = naics
        if url is not None:
            self.url = url
        
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @property
    def agency(self):
        return self._agency

    @agency.setter
    def agency(self, agency):
        self._agency = agency

    @property
    def posted_date(self):
        return self._posted_date

    @posted_date.setter
    def posted_date(self, posted_date):
        self._posted_date = posted_date

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    @property
    def set_aside(self):
        return self._set_aside

    @set_aside.setter
    def set_aside(self, set_aside):
        self._set_aside = set_aside

    @property
    def due_date(self):
        return self._due_date

    @due_date.setter
    def due_date(self, due_date):
        self._due_date = due_date

    @property
    def naics(self):
        return self._naics

    @naics.setter
    def naics(self, naics):
        self._naics = naics

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(OppDto, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, OppDto):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
