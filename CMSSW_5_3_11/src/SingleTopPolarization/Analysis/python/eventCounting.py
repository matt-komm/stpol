
import FWCore.ParameterSet.Config as cms

"""
This method inserts an EventCountProducer before and after the given Sequence,
thus counting the efficiency of event selection in this sequence.
"""
def countInSequence(process, path):
	pathName = path.label()
	preCountName = pathName + "PreCount"
	postCountName = pathName + "PostCount"
	setattr(process, preCountName, cms.EDProducer("EventCountProducer"))
	setattr(process, postCountName, cms.EDProducer("EventCountProducer"))
	path.insert(0, getattr(process, preCountName))
	path.insert(-1, getattr(process, postCountName))

"""
Counts the number of events after the specified processes with a path-unique counter
"""
def countAfter(process, path, processes):
    for p in processes:
        countName = path.label() + p[0].upper() + p[1:] + "PostCount"
        counter = cms.EDProducer("EventCountProducer")
        setattr(process, countName, counter)
        path.insert(path.index(getattr(process, p)) + 1, counter)

def countProcessed(process):
	countName = process.name_() + "TotalEventsProcessedCount"
	counter = cms.EDProducer("EventCountProducer")
	setattr(process, countName, counter)
	process.totalEventCounterPath = cms.Path(counter)