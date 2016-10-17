from workflows import WorkflowStep
from copy import deepcopy
from .classes.NMRSpectrum import NMRSpectrum
import traceback

class WFManager:
    @classmethod
    def excuteSteps(cls, steps, seed):
        #traceback.print_stack(limit=4)
        return reduce(lambda x, y: y(x), steps, seed)
    
    @classmethod
    def computeStep(cls, step, spec):
        if _islocked('no_transpose', spec):
            traceback.print_stack()
        wf = deepcopy(spec.history)
        all_steps = wf._steps
        idx, replace = wf._get_order_idx(step)
        
        
        before_idx = after_idx = idx
        if replace:
            after_idx += 1
        
        last = after_idx == len(all_steps)
        
        if before_idx == len(all_steps):
            input_ = spec
        else:
            input_ = spec.setData( cls.excuteSteps(all_steps[:before_idx], spec.original) )
            
            
        ret = step(input_)
        # If the function returned a computed step, execute it.
        if isinstance(ret, WorkflowStep):
            step._computed = ret._computed
            ret = step(input_)
        
        
        # If the function returned the processed spectrum, 
        # write the original function and arguments in the history.
        if isinstance(ret, NMRSpectrum):
            if ret.history._stepnames != wf._stepnames and (not ret.history.empty()):
                # The function modified the history itself.
                # history contains at least one operation.
                
                return ret # we trust the function.
            
            # By now, ret.history either contains the input_ history or is empty
            # If the step was inserted in the middle of the workflow, excute the
            # rest of the steps.
            if len(all_steps[after_idx:]) > 0:
                output_ = cls.excuteSteps(all_steps[after_idx:], ret)
                ret = ret.setData(output_)
            
            # Add the step to the worflow
            wf.append(step)
            ret.history = wf
         
        return ret
        
def _islocked(lock_name, s):
    if hasattr(s, 'spec_flags') and s.spec_flags.has_key(lock_name):
        return s.spec_flags[lock_name]
    
    return False