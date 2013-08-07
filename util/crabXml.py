from xml.dom.minidom import parse
import numpy
#from collections import OrderedDict as dict
import time
import datetime
import sys
import glob
import scipy
import scipy.stats
import scipy.stats.mstats
import pdb
import math
import re

class TimeStats:
    def __init__(self, minimum, maximum, mean, quantiles):
        self.minimum = minimum
        self.maximum = maximum
        self.mean = mean
        self.quantiles = quantiles

    def __str__(self):
        s = "min=%s max=%s mean=%s quantiles[0.25, 0.5, 0.75, 0.95]=%s" % (self.minimum, self.maximum, self.mean, [str(s) for s in self.quantiles])
        return s
class JobStats:
    def __init__(self, task):
        completed = filter(lambda j: j.isCompleted(), task.jobs)
        needs_get = filter(lambda j: j.needsGet(), task.jobs)
        pending = filter(lambda j: j.isPending(), task.jobs)
        needs_submit = filter(lambda j: j.isCreated(), task.jobs)
        if len(task.jobs)>0:
            quantiles_submissions = scipy.stats.mstats.mquantiles(map(lambda j: j.n_submission, task.jobs), prob=[0.25, 0.5, 0.75, 0.95])
            self.quantiles_submissions = [int(x) for x in quantiles_submissions]
            max_submissions = numpy.max(map(lambda j: j.n_submission, task.jobs))
        else:
            self.quantiles_submissions = None
            max_submissions = None

        needs_resubmit = filter(lambda j: j.needsResubmit(), task.jobs)
        self.jobs_total = len(task.jobs)
        self.jobs_completed = len(completed)
        self.jobs_to_get = len(needs_get)
        self.jobs_to_submit = len(needs_submit)
        self.jobs_pending = len(pending)
        self.jobs_to_resubmit = len(needs_resubmit)
        self.max_submissions = max_submissions
        self.time_stats_success =  Task.timeStats(filter(lambda x: x.isCompleted(), task.jobs))
        if self.time_stats_success:
            self.total_time = self.time_stats_success.mean * len(completed)
        else:
            self.total_time = None
        self.time_stats_fail = Task.timeStats(filter(lambda x: x.needsResubmit(), task.jobs))
        self.fail_codes = Task.retCodes(filter(lambda x: x.needsResubmit(), task.jobs))
        self.name = task.name

    def summary(self):
        s = "%s: (tot %d| comp %d| PD %d | RS %d | S %d) | %.2f %%" % (
            self.name, self.jobs_total, self.jobs_completed, self.jobs_pending,
            self.jobs_to_resubmit, self.jobs_to_submit,
            100.0*(float(self.jobs_completed) / float(self.jobs_total)) if self.jobs_total>0 else 0,
        )
        if self.jobs_total != (self.jobs_pending + self.jobs_completed + self.jobs_to_resubmit + self.jobs_to_submit):
            s = ">>>" + s
        return s
    def __str__(self):
        s = self.name
        s += "\nJobs: tot %d, comp %d , get %d, resub %d, pending %d\n, not submitted %d" % (
            self.jobs_total,
            self.jobs_completed,
            self.jobs_to_get,
            self.jobs_to_resubmit,
            self.jobs_pending,
            self.jobs_to_submit
        )
        s += "Submissions: quantiles[0.25, 0.5, 0.75, 0.95]=%s, max %d\n" % (self.quantiles_submissions, self.max_submissions)
        s += "Successful job timing: %s\n" % str(self.time_stats_success)
        s += "Failed job timing: %s\n" % str(self.time_stats_fail)
        s += "Return codes for failed: %s\n" % str(self.fail_codes)
        s += "Total time used so far (approx.): %s\n" % str(self.total_time)
        return s

class Task:
    def __init__(self, fname=None):
        self.prev_jobs = []
        self.jobs = []
        self.name = ""
        self.fname = ""
        if fname:
            self.updateJobs(fname)

    def isCompleted(self):
        for job in self.jobs:
            if not job.isCompleted():
                return False
        return True

    def __add__(self, other):
        new_task = Task()
        new_task.jobs = self.jobs + other.jobs
        new_task.name = self.name + " and " + other.name
        return new_task

    @staticmethod
    def parseJob(args):
        job, running_job = args
        id = get(job, "jobId", int)
        name = get(job, "name", str)
        submission = get(running_job, "submission", int)
        schedulerId = get(running_job, "schedulerId", str)
        submissionTime = get(running_job, u'submissionTime', str)
        outputFiles = get(job, "outputFiles", str)
        if outputFiles:
            outputFiles = outputFiles.split(",")
        else:
            outputFiles = []
        getOutputTime = get(running_job, "getOutputTime", str)
        try:
            wrapperReturnCode = get(running_job, "wrapperReturnCode", int)
        except ValueError:
            wrapperReturnCode = -1
        try:
            applicationReturnCode = get(running_job, "applicationReturnCode", int)
        except:
            applicationReturnCode = None

        lfn = get(running_job, "lfn", str)
        if lfn:
            lfn = lfn[2:-2]
        state = get(running_job, "state", str)
        return Job(
            name, id, submission, schedulerId,
            submissionTime, getOutputTime, applicationReturnCode,
            wrapperReturnCode, state, lfn, outputFiles
        )


    def updateJobs(self, fname):
        try:
            dom = parse(fname)
        except Exception as e:
            print "Failed to parse xml %s" % fname
            print e
            return
        self.fname = fname

        self.output_dir = get(dom.getElementsByTagName("TaskAttributes")[0], "outputDirectory", str)

        jobs_a = dom.getElementsByTagName("Job")
        jobs_b = dom.getElementsByTagName("RunningJob")
        if len(jobs_a)==0 or len(jobs_b) == 0 or len(jobs_a) != len(jobs_b):
            self.prev_jobs = []
            self.jobs = []
        else:
            self.prev_jobs = self.jobs
            self.jobs = map(Task.parseJob, zip(jobs_a, jobs_b))
        self.name = re.match(".*WD_(.*)/share/RReport.xml", self.fname).group(1)

    @staticmethod
    def timeStats(jobs):
        times = map(
            lambda j: j.totalTime().seconds,
            jobs
        )
        if len(times)==0:
            return None
        quantiles_time = [datetime.timedelta(seconds=int(x)) for x in scipy.stats.mstats.mquantiles(times, prob=[0.25, 0.5, 0.75, 0.95])]
        mean_time = datetime.timedelta(seconds=int(numpy.mean(times)))
        min_time = datetime.timedelta(seconds=int(numpy.min(times)))
        max_time = datetime.timedelta(seconds=int(numpy.max(times)))
        return TimeStats(min_time, max_time, mean_time, quantiles_time)

    @staticmethod
    def retCodes(jobs):
        rets = dict()
        for j in jobs:
            if (j.wrapper_ret_code, j.app_ret_code) not in rets.keys():
                rets[(j.wrapper_ret_code, j.app_ret_code)] = 0
            rets[(j.wrapper_ret_code, j.app_ret_code)] += 1
        return rets

    def printStats(self):
        stats = JobStats(self)
        print str(stats), self.fname

def maketime(s):
    if s:
        return datetime.datetime.fromtimestamp(time.mktime(time.strptime(s, "%Y-%m-%d %H:%M:%S")))
    else:
        return None
class Job:
    def __init__(self,
        name,
        job_id,
        n_submission,
        scheduler_id,
        submission_time,
        get_output_time,
        wrapper_ret_code,
        app_ret_code,
        state,
        lfn,
        outputFiles
    ):
        self.name = name
        self.job_id = job_id
        self.n_submission = n_submission
        self.scheduler_id = scheduler_id
        self.submission_time = maketime(submission_time)
        self.get_output_time = maketime(get_output_time) if get_output_time is not None else None
        self.wrapper_ret_code = wrapper_ret_code if wrapper_ret_code is not None else -1
        self.app_ret_code = app_ret_code if app_ret_code is not None else -1
        self.state = state
        self.lfn = lfn
        self.outputFiles = outputFiles

    def isCompleted(self):
        return self.wrapper_ret_code == 0 and self.app_ret_code == 0

    def isCreated(self):
        return self.state == "Created"

    def needsGet(self):
        return self.state == "Terminated"

    def isPending(self):
        return self.state == "SubSuccess"

    def needsResubmit(self):
        return (self.state == "Cleared" or self.state=="Terminated") and not self.isCompleted()

    def totalTime(self):
        t1 = self.get_output_time if self.get_output_time else datetime.datetime.now()
        if self.submission_time and t1:
            return t1 - self.submission_time
        else:
            return -1

    def __repr__(self):
        return "Job(%d, %s)" % (
            self.job_id,
            self.scheduler_id,
        )

def get(node, name, f):
    item = node.attributes.getNamedItem(name)
    if item is None:
        return None
    else:
        return f(item.nodeValue)

if __name__=="__main__":
    reports = sys.argv[1:]
    print "reports=",reports
    reports = sorted(reports)

    t_tot = Task()
    completed = []
    for r in reports:
        t = Task()
        t.updateJobs(r)
        js = JobStats(t)
        match = re.match("(.*)/WD_(.*)/share/RReport.xml", r)
        if not match:
            raise ValueError("Couldn't understand pattern: %s" % r)
        filelist_path = match.group(1) + "/" + match.group(2) + ".files.txt"
        of = open(filelist_path, "w")
        for job in t.jobs:
            if job.isCompleted() and job.lfn:
                of.write(job.lfn + "\n")
        of.close()
        if t.isCompleted():
            completed.append(t)
        print js.summary(), t.fname
        t_tot += t
    tot_stats = JobStats(t_tot)
    tot_stats.name = "total"
    print tot_stats.summary()
    print "--- total ---"
    print str(tot_stats)

    print "--- Completed ---"
    for t in completed:
        print "/".join(t.fname.split("/")[:-2])
