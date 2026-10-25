"""Domain layer of the rosenlund Home Assistant automation stack.

Framework-independent Python policy package. Adapters (currently the YAML
automations on the HA VM) translate HA state into the domain inputs and
translate the results back into service calls. The domain must stay free of
Home Assistant imports, entity IDs, and side effects.
"""

__version__ = "0.1.0"
