#!/usr/bin/env python3
# -*- coding=utf-8 -*-

"""The Product section."""

from termcolor import colored

from core.front.classes.globals import BaseSection
from core.back.database.data_wrapper import datas_wrapper as datas
import textwrap


class Product(BaseSection):
    """The product class."""

    def __init__(self):
        """Initialization."""
        super().__init__()

        self.name = datas.chosen_product.upper()

        self.c_return_prd = "[return prod]: return to the products page.\n"

    @property
    def header(self):
        """Return the header informations."""
        title = f"   {self.name}"
        return colored(title, "yellow") + "\n" + "   " + "-" * 23

    @property
    def content(self):
        """Return the content."""
        content = datas.load_product()
        # substituts = datas.load_substituts()
        text = ""
        titles = ("name: ", "description: ",
                  "stores ", "url: ", "nutri-score: ")

        for title, infos in zip(titles, content):
            infos = textwrap.wrap(str(infos), 45)
            infos = "\n     ".join(infos)
            text += ("   * " + colored(title, "yellow") + infos + " \n")
        return text

    @property
    def footer(self):
        """Return the footer informations.

        Call 'super().footer' to get the error messages.
        """
        return (self.comm + self.c_return_prd + self.c_return_ctgs +
                self.c_quit + "\n") + super().footer

    @property
    def actions(self):
        """Return the possible actions.

        Call 'super().actions' to get the basic actions.
        """
        return (self.a_return_ctgs + ["return prod"] + super().actions)

    def apply(self, action):
        """Apply an action."""
        if action == "return cat":
            self.change_to = "Categories"
        if action == "return prod":
            self.change_to = "Category"
