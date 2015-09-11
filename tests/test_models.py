#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_models
----------------------------------

Tests for `teamsupport.models` module.
"""
import unittest

from lxml.builder import E

from teamsupport.errors import MissingArgumentError
from teamsupport.models import Action, Ticket
from tests import BaseTeamSupportServiceCase


class TestTicket(BaseTeamSupportServiceCase):
    def setUp(self):
        super(TestTicket, self).setUp()
        self.ticket_elemet = E.Ticket(E.TicketID('ID'))

    def test_initialisation_with_id(self):
        self.response.content = '<Ticket><TicketID>ID</TicketID></Ticket>'

        ticket = Ticket(self.client, ticket_id='ID')
        self.assertEqual(ticket.id, 'ID')

    def test_initialisation_with_data(self):
        ticket = Ticket(self.client, data=self.ticket_elemet)
        self.assertEqual(ticket.id, 'ID')

    def test_initialisation_fails_when_missing_args(self):
        self.assertRaises(MissingArgumentError, Ticket, self.client)

    def test_getattr(self):
        ticket_element = E.Ticket(E.TicketID('ID'), E.Field2('Test'))
        ticket = Ticket(self.client, data=ticket_element)
        self.assertEqual(ticket.Field2, 'Test')

    def test_actions_property(self):
        self.response.content = """<Actions>
            <Action>
                <ID>ActionID</ID>
                <TicketID>ID</TicketID>
                <Name>Description</Name>
            </Action>
        </Actions>"""

        ticket = Ticket(self.client, data=self.ticket_elemet)

        actions = ticket.actions
        self.assertEqual(len(actions), 1)
        self.assertIsInstance(actions[0], Action)
        self.assertEqual(actions[0].id, 'ActionID')
        self.assertEqual(actions[0].ticket_id, 'ID')
        self.assertEqual(actions[0].Name, 'Description')

    def test_actions_querylist(self):
        self.response.content = """<Actions>
                <Action>
                    <ID>ActionID</ID>
                    <TicketID>ID</TicketID>
                    <Name>Description</Name>
                </Action>
            </Actions>"""

        ticket = Ticket(self.client, data=self.ticket_elemet)

        actions = ticket.actions
        description_action = actions.get(Name='Description')
        self.assertIsInstance(description_action, Action)
        self.assertEqual(description_action.id, 'ActionID')
        self.assertEqual(description_action.ticket_id, 'ID')


class TestAction(BaseTeamSupportServiceCase):
    def setUp(self):
        super(TestAction, self).setUp()
        self.action_element = E.Action(
            E.ID('ActionID'),
            E.TicketID('ID'),
            E.Name('Description'))

    def test_initialisation_with_ids(self):
        self.response.content = """<Action>
                <ID>ActionID</ID>
                <TicketID>ID</TicketID>
                <Name>Description</Name>
            </Action>"""

        action = Action(self.client, ticket_id='ID', action_id='ActionID')
        self.assertEqual(action.ticket_id, 'ID')
        self.assertEqual(action.id, 'ActionID')

    def test_initialisation_with_data(self):
        action = Action(self.client, data=self.action_element)
        self.assertEqual(action.ticket_id, 'ID')
        self.assertEqual(action.id, 'ActionID')

    def test_initialisation_fails_when_missing_args(self):
        self.assertRaises(MissingArgumentError, Action, self.client)
        self.assertRaises(MissingArgumentError, Action, self.client,
                          ticket_id='ID')
        self.assertRaises(MissingArgumentError, Action, self.client,
                          action_id='ActionID')


if __name__ == '__main__':
    unittest.main()
