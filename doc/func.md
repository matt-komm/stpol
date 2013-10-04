Functional specification
========================

# Event-level methods
These methods take an abstract Event as input and return the corresponding value for the Event. The Event type depends on the backend and can be for example ``fwlite::(Chain)Event``, a tuple of ``run``, ``lumi``, ``event`` id-s etc.

## `stpol.stable.tchan.signallepton`

## `stpol.stable.tchan.muon`

* `pt, eta, phi, reliso (float)`
* `id (int)`: the gen-level particle id (Pythia scheme)
* `globaltrack (int)`
* `innertrack (int)`

## `stpol.stable.tchan.electron`

* `pt, eta, phi, reliso (float)`
* `id (int)`: the gen-level particle id (Pythia scheme)
* `mvaid`

## `stpol.stable.tchan.wtbjet`

The (b-tagged) jet associated with the decay t -> W b

* `pt, eta, phi, reliso (float)`
* `id (int)`: the gen-level particle id (Pythia scheme)

## `stpol.stable.tchan.specjet1`

The jet taken to be from the recoling light quark. Used for the spin basis.

* `pt, eta, phi, mass (float)`
* `mvaid (float)`

## `stpol.stable.tchan.specjet2,3...`

Other spectator jets not associated with any leg in the t-channel diagram. Ordered by pt descending.

* `pt, eta, phi, mass (float)`

## `stpol.stable.event`

Overall event-level parameters.

* `met`: the missing transverse energy

## `stpol.stable.event.costheta`

Angular variables associated with the Wtb vertex.

* `lj`: the angle between the charged lepton and the b-jet in the spectator jet basis
* `bl`: the angle in the eta-beamline basis

## Description of backends
### FWLite C++
### Python
### Julia
