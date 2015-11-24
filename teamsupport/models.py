from property_caching import cached_property
from querylist import QueryList

from teamsupport.services import TeamSupportService
from teamsupport.errors import MissingArgumentError


ACTION_TYPE_DESCRIPTION = 1


class XmlModel(object):
    def __getattr__(self, name):
        if self.data.find(name) is not None:
            return self.data.find(name).text
        raise AttributeError(name)

    @classmethod
    def get_client(cls):
        return TeamSupportService()

    @cached_property
    def client(self):
        return self.get_client()


class Ticket(XmlModel):
    TICKET_STATUS_NEW = None
    TICKET_TYPE_SUPPORT = None

    def __init__(self, ticket_id=None, data=None):
        self.data = data
        if ticket_id:
            self.data = self.client.get_ticket(ticket_id)
        elif not self.data:
            raise MissingArgumentError(
                "__init__() needs either a 'ticket_id' or 'data' argument "
                '(neither given)')
        self.id = self.TicketID

    @classmethod
    def create(
            cls, user_email, user_first_name, user_last_name,
            title, description, **params):
        # We need to associate ticket with Contact, otherwise ticket doesn't
        # make sense. First, we try to find an existing contact.
        contact = Contact.get(user_email)
        if contact is None:
            # Otherwise - create new one.
            contact = Contact.create(
                user_email, FirstName=user_first_name,
                LastName=user_last_name
            )

        data = {
            'Name': title,
            'TicketStatusID': cls._get_ticket_status_new(),
            'TicketTypeID': cls._get_ticket_type_support(),
            'ContactID': contact.id
        }

        ticket = Ticket(data=cls.get_client().create_ticket(data))
        ticket.set_description(description)
        return ticket

    @classmethod
    def _get_ticket_status_new(cls):
        if cls.TICKET_STATUS_NEW is not None:
            return cls.TICKET_STATUS_NEW

        statuses = cls.get_client().get_ticket_statuses()
        for status in statuses:
            if status.find('Name').text.lower() == 'new':
                cls.TICKET_STATUS_NEW = status.find('TicketStatusID').text
                return cls.TICKET_STATUS_NEW

    @classmethod
    def _get_ticket_type_support(cls):
        if cls.TICKET_TYPE_SUPPORT is not None:
            return cls.TICKET_TYPE_SUPPORT

        ticket_types = cls.get_client().get_ticket_types()
        for ticket_type in ticket_types:
            if ticket_type.find('Name').text.lower() == 'support':
                cls.TICKET_TYPE_SUPPORT = ticket_type.find(
                    'TicketTypeID').text
                return cls.TICKET_TYPE_SUPPORT

    def delete(self):
        self.client.delete_ticket(self.id)

    def get_description(self):
        ticket_actions = self.client.get_ticket_actions(
            self.id, SystemActionTypeID=ACTION_TYPE_DESCRIPTION)
        if len(ticket_actions) >= 1:
            return ticket_actions[0].find('Description').text
        return None

    def set_description(self, description):
        # Description is an Action in TeamSupport API. That action is created
        # automatically when the ticket is created. We need to query it's ID
        # and update this action to set ticket description.
        ticket_actions = self.client.get_ticket_actions(
            self.id, SystemActionTypeID=ACTION_TYPE_DESCRIPTION)
        action_id = ticket_actions[0].find('ActionID').text
        self.client.update_ticket_action(
            self.id, action_id, {'Description': description})

    @cached_property
    def actions(self):
        actions = self.client.get_ticket_actions(self.id)
        return QueryList(
            [Action(data=action)
                for action in actions.findall('Action')], wrap=False)

    @cached_property
    def contacts(self):
        contacts = self.client.get_ticket_contacts(self.id)
        return QueryList(
            [Contact(data=contact)
                for contact in contacts.findall('Contact')], wrap=False)

    @cached_property
    def customers(self):
        customers = self.client.get_ticket_customers(self.id)
        return QueryList(
            [Customer(data=customer)
                for customer in customers.findall('Customer')], wrap=False)


class Action(XmlModel):
    def __init__(self, ticket_id=None, action_id=None, data=None):
        self.data = data
        if action_id and ticket_id:
            self.data = self.client.get_ticket_action(ticket_id, action_id)
        elif not self.data:
            raise MissingArgumentError(
                "__init__() needs either both a 'ticket_id' and 'action_id' "
                "or a 'data' argument (neither given)")
        self.ticket_id = self.TicketID
        self.id = self.ID


class Contact(XmlModel):
    def __init__(self, data):
        self.data = data
        self.id = self.ContactID

    @classmethod
    def get(cls, email):
        """Return first contact with given email."""
        client = cls.get_client()
        contacts = client.search_contacts(Email=email)
        if len(contacts) >= 1:
            return Contact(data=contacts[0])
        return None

    @classmethod
    def create(self, email, **data):
        client = self.get_client()
        contact_data = {'Email': email}
        contact_data.update(data)
        contact_xml = client.create_contact(contact_data)
        return Contact(data=contact_xml)

    def delete(self):
        self.client.delete_contact(self.id)


class Customer(XmlModel):
    def __init__(self, data):
        self.data = data
        self.id = self.OrganizationID

    @cached_property
    def contacts(self):
        contacts = self.client.get_customer_contacts(self.id)
        return QueryList(
            [Contact(data=contact)
                for contact in contacts.findall('Contact')], wrap=False)
