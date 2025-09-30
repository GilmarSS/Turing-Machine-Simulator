import json
import sys

class TuringMachine:
    def __init__(self, spec_file):
        with open(spec_file, 'r') as f:
            spec = json.load(f)
            
        self.initial_state = str(spec['initial'])
        
        self.accept_state = str(spec['final'][0])
        
        self.reject_state = 'q_rej' 
        self.blank_symbol = spec['white']
        
        self.transitions = self._format_transitions(spec['transitions'])

        self.current_state = self.initial_state
        self.tape = []
        self.head_position = 0
        self.steps_taken = 0 
        
    def _format_transitions(self, raw_transitions):
        formatted = {}
        for t in raw_transitions:
            key = f"{t['from']},{t['read']}"
            formatted[key] = [str(t['to']), t['write'], t['dir']]
        return formatted
        
    def load_input(self, input_file):
        with open(input_file, 'r') as f:
            input_string = f.read().strip()
            self.tape = list(input_string)
            
        self.tape.insert(0, self.blank_symbol)
        self.tape.append(self.blank_symbol)
        self.head_position = 1
        
    def step(self):
        self.steps_taken += 1
        tape_view = "".join(self.tape).strip(self.blank_symbol)
        print(f"Passo: {self.steps_taken} | Estado: {self.current_state} | Pos: {self.head_position} | Lido: {self.tape[self.head_position]} | Fita: {tape_view}")
        
        current_symbol = self.tape[self.head_position]
        transition_key = f"{self.current_state},{current_symbol}" 
        
        if transition_key in self.transitions:
            new_state, new_symbol, move = self.transitions[transition_key]

            self.tape[self.head_position] = new_symbol
            self.current_state = new_state

            if move == 'R':
                self.head_position += 1
            elif move == 'L':
                self.head_position -= 1

            if self.head_position == len(self.tape):
                self.tape.append(self.blank_symbol)
            elif self.head_position < 0:
                self.tape.insert(0, self.blank_symbol)
                self.head_position = 0
            
            return True
        else:
            return False

    def run(self, max_steps=20000):
        steps = 0
        
        while self.current_state not in [self.accept_state, self.reject_state] and steps < max_steps:
            if not self.step():
                self.current_state = self.reject_state
                break 
            steps += 1

        if self.current_state == self.accept_state:
            return 1, self.get_output_tape()
        elif self.current_state == self.reject_state:
            return 0, self.get_output_tape()
        else:
            return 0, "TIMEOUT"

    def get_output_tape(self):
        start = 0
        while start < len(self.tape) and self.tape[start] == self.blank_symbol:
            start += 1
        
        end = len(self.tape) - 1
        while end >= 0 and self.tape[end] == self.blank_symbol:
            end -= 1

        if start <= end:
            return "".join(self.tape[start:end+1])
        else:
            return ""

# ----------------------------------------------------
# Função Principal (Main)
# ----------------------------------------------------
if __name__ == '__main__':
    
    if len(sys.argv) != 3:
        print("Uso: python turing_machine_simulator.py <arquivo_json> <arquivo_txt_entrada>")
        sys.exit(1)
        
    spec_file = sys.argv[1]
    input_file = sys.argv[2]
    output_file = "fita_saida.txt"
    
    try:
        mt = TuringMachine(spec_file)
        mt.load_input(input_file)
        result, output_tape = mt.run()
        
        print(result) 
        
        with open(output_file, 'w') as out_f:
            out_f.write(output_tape)
            
    except FileNotFoundError as e:
        print(f"Erro: Arquivo não encontrado: {e}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Erro: O arquivo de especificação JSON '{spec_file}' é inválido.")
        sys.exit(1)
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a simulação ou leitura: {e}")
        sys.exit(1)