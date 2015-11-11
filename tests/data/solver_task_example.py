

task_template = '''
My name is {{username}}.
I have {{total}} $. I want to buy several papers.
Each paper worth is {{paper_cost}}$.
How much papers can I buy?'''

task_code_preamble = ''' 
import this
'''

task_code_postamble='''
OUTPUTS['postamvle'] = myvalue
'''

task_code = '''
OUTPUTS['result']=int(INPUTS['total']/INPUTS['paper_cost'])
'''

task_solution_template = '''
Answer is {{result}}.
'''

task_defaults = {'username' : 'dmitry', 'total' : 100, 'paper_cost' : 20}
