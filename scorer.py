import os
import json
import argparse
import model
from pathlib import Path
from tqdm import tqdm

data = {}
def get_response(C, model_name, q_id, img_path, question):
    ans = model.get_response(img_path, question)
    # Record the model's answer
    if model_name in data :
        data[model_name][q_id] = ans
    else: 
        data[model_name] = {}
        data[model_name][q_id] = ans

score = {}        
def eval_model(res_file, gt_file, C, sav):
    # Load model predictions
    with open(res_file, 'r', encoding='utf-8') as file:
        res = json.load(file)
    # Load ground-truth 
    with open(gt_file, 'r', encoding='utf-8') as file:
        gt = json.load(file)
    
    for model_name, ans_list in res.items():
        sum = 0
        for q_id, ans in ans_list.items():
            if ans[0].upper() == gt[q_id]: sum += 1
        
        score[model_name] = sum * 100 / 675
        print(f"The score of model_name is: {score[model_name]}")
    
    # Save the score
    Path("scores").mkdir(exist_ok=True)
    Path(f"scores/{C}T1subtask").mkdir(exist_ok=True)
    with open(f"./scores/{C}T1subtask/{filename}.json", 'w', encoding='utf-8') as file:
        json.dump(score, file, ensure_ascii=False, indent=4)
    
def get_args():
    parser = argparse.ArgumentParser(description="Evaluate models")
    parser.add_argument('--subtask', '-s', required=True, choices=['4','7','10'], 
                        help="Select the benchmark subtask with different options 4, 7, or 10")
    parser.add_argument('--filename', '-f', type=str, required=True, help="Filename used to save or load results")
    parser.add_argument('-y1', action="store_true", 
                        help="If set, directly evaluate existing results instead of running the model.")
    parser.add_argument('--model_name', '-m', type=str, default="the model", help="Specify the evaluated model's name")
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    C = args.subtask
    filename = args.filename
    y1 = args.y1
    model_name = args.model_name

    # Load samples of for the subtask
    with open(f'./benchmark/{C}T1subtask/question.json', 'r', encoding='utf-8') as file:
        question = json.load(file)
    # Load the prompt template for the subtask
    with open(f"./prompt_template/question_{C}.txt", 'r', encoding='utf-8') as file:
        T = file.read()    
    
    if y1: # Evaluate existing results from files without running the model
        eval_model(f"./results/{C}T1subtask/{filename}.json", f'./benchmark/{C}T1subtask/gt.json', C, filename)
        print("EVALUATED!")
    
    else : # Run the model to produce results
        model.load()
        for i in tqdm(range(1, 676)):
            img_path = f'./benchmark/{C}T1subtask/pic/{i}.png'
            D = question[str(i)]
            Q = T.replace("<question>", D["QUESTION"]).replace("<option>",D["OPTIONS"])
            get_response(C, model_name, i, img_path, Q)
 
        Path("results").mkdir(exist_ok=True)
        Path(f"results/{C}T1subtask").mkdir(exist_ok=True)
        with open(f"./results/{C}T1subtask/{filename}.json", 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        eval_model(f"./results/{C}T1subtask/{filename}.json", f'./benchmark/{C}T1subtask/gt.json', C, filename)
        print("EVALUATED!")