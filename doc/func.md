Functional specification
========================

# Event-level methods

All of these methods adhere to the following pattern (in pseudocode to show types)

    float pt(const event)
        ... //Gets the value of pt
        return x
    end

The underlying event is accessed to calculate/retrieve the variable of interest.
The return types are specified using `pt -> rettype`. 

## `stpol.stable.tchan.muon`

### Generic for leptons

* `pt, eta, phi, mass, reliso -> float`
* `id -> int`: the gen-level particle id (Pythia scheme)
* `mtw -> float`: the transverse mass of the lepton+MET system
* `charge -> int`

### Specific for muons

* `globaltrack -> int`
* `innertrack -> int`

## `stpol.stable.tchan.electron`

### Generic for leptons

(as above)

### Specific for electrons

* `mvaid`

## `stpol.stable.tchan.vetolepton`

* `pt, eta, phi, mass, reliso -> float`
* `id -> int`: the gen-level particle id (Pythia scheme)
* `charge -> int`

## `stpol.stable.tchan.bjet`

The (b-tagged) jet associated with the decay t -> W b

* `pt, eta, phi, reliso -> float`
* `id -> int`: the gen-level particle id (Pythia scheme). In general assigned via the PAT mechanisms for parton flavour.
* `dr -> float`: the ΔR with respect to the isolated lepton in the event
* `pu_mvaid -> float`: the pile-up MVA id
* `bd_csv -> float`: the CSV b-discriminator
* `bd_tchp -> float`: the TCHP b-discriminator

## `stpol.stable.tchan.specjet1`

The jet taken to be from the recoiling light quark. Used for the spin basis.
See `stpol.stable.tchan.bjet` for the interface.

## `stpol.stable.tchan.specjet2,3...`

Other spectator jets not associated with any leg in the t-channel diagram. Ordered by pt descending.
See `stpol.stable.tchan.bjet` for the interface.

## `stpol.stable.event`

Overall event-level parameters.

* `met`: the missing transverse energy
* `c`: centrality
* `njets`: the number of good jets passing the jet ID
* `ntags`: the number of good jets passing the jet ID *** and *** the default b-tagging working point used in the analysis.
* `ismu -> bool`: is the event a muon event
* `isele -> bool`: is the event an electron event

## `stpol.stable.event.costheta`

Angular variables associated with the Wtb vertex.

* `lj`: the angle between the charged lepton and the b-jet in the spectator jet basis
* `bl`: the angle in the eta-beamline basis

## Description of backends

These methods take an abstract Event as input and return the corresponding value for the Event. The Event type depends on the backend and can be for example ``fwlite::(Chain)Event``, a tuple of ``run``, ``lumi``, ``event`` id-s etc.

### FWLite C++
### Python
### Julia
