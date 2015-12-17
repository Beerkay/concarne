.. concarne documentation master file, created by
   sphinx-quickstart on Thu Dec 17 14:16:07 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to concarne's documentation!
====================================

Contents:

.. toctree::
   :maxdepth: 2


API Reference
====================================

.. automodule:: concarne

Patterns
--------

.. toctree::
  :maxdepth: 3

.. autoclass:: concarne.patterns.Pattern
    :members:

Single Patterns
~~~~~~~~~~~~~~~

.. autoclass:: concarne.patterns.DirectPattern
    :members:

.. autoclass:: concarne.patterns.MultiTaskPattern
    :members:
    
.. autoclass:: concarne.patterns.MultiViewPattern
    :members:

Pairwise Patterns
~~~~~~~~~~~~~~~
    
.. autoclass:: concarne.patterns.PairwiseTransformationPattern
    :members:
    
.. autoclass:: concarne.patterns.PairwisePredictTransformationPattern
    :members:

PatternTrainer
--------
.. toctree::
  :maxdepth: 2

.. autoclass:: concarne.training.PatternTrainer
    :members:


Iterators
--------
.. toctree::
  :maxdepth: 2

.. autoclass:: concarne.iterators.AlignedBatchIterator
    :members:
    
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
