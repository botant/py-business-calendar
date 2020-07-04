Introduction
============

Background
----------

Python's built-in datetime functionality is very basic only works for general
purpose applications or as a framework to be built upon.

**Business Calendar** calculations is an example of missing functionality. It
is so important for financial applications and yet not easy to find. Many other
packages offer some of the functionality needed but not the all, so I decided
to put together a small class that did everything I wanted and hopefully other
people will find it useful as well.

Comparison
----------

Many packages have date functions that are very interesting but didn't suit
my needs in financial applications. I've tried to list some them here so you
can decide what is best for you:

**dateutil**:
    A great package with many functions that will let you generate any sort of
    date list. Dateutil includes `relativedelta` that extend the calculations
    in the built-in `datetime`. I tried to use it to calculate things like date
    offsets with holidays and number of business days between two dates, and I
    found that generating a huge list and searching wasn't ideal. It is my
    benchmark, and I use it in the unit tests to make sure the calculations are
    correct.

**numpy**:
    Numpy added datetime functionality in version 1.7. It has the main things
    I was looking for (`is_busday`, `busday_offset` and `busday_count`), and
    it can handle holidays, but I was put off by two things:

    * The docs say the API is experimental. Nothing wrong with that because
      numpy is a super package that must cater to all sorts of scientific
      applications, but I needed something simple and stable.
    * It works on numpy native dates, which are different from datetime and
      don't work with *sqlalchemy*, for example.

**pandas**:
    Pandas' date functionality uses the best features from `dateutil` and
	`numpy`, which means it inherits their problems as well. The pandas class
    `CustomBusinessDay` is based on `numpy.busdaycalendar` and it is still in
    its adolescence. It also works on Pandas native date type which has to be
    converted back and forth when interacting with other libraries.

Quick usage
-----------

.. literalinclude:: ../business_calendar/example/example.py

Contents
--------

.. toctree::

   cal
   license
