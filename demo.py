import gradio as gr
import boto3
from botocore.config import Config
import json
from translate import GuideBased
import re
from ape import APE
ape = APE()
rewrite = GuideBased()

def generate_prompt(original_prompt, level):
    if level == '一次生成':
        result = rewrite(original_prompt) #, cost
        return [gr.Textbox(label="我们为您生成的prompt",
                   value=result,
                   lines=3,show_copy_button=True,interactive=False)]+[gr.Textbox(visible=False)]*2
        
    elif level == '多次生成':
        candidates = []
        for i in range(3):
            result = rewrite(original_prompt)
            candidates.append(result)
        judge_result = rewrite.judge(candidates)
        textboxes = []
        for i in range(3):
            is_best = 'Y' if judge_result == i else 'N'
            textboxes.append(
                gr.Textbox(label=f"我们为您生成的prompt #{i+1} {is_best}",
                   value=candidates[i],
                   lines=3,show_copy_button=True,visible=True,interactive=False)
            )
        return textboxes

def ape_prompt(original_prompt, user_data):
    result = ape(initial_prompt, 1, json.loads(user_data))
    return [gr.Textbox(label="我们为您生成的prompt",
                       value=result['prompt'],
                       lines=3,show_copy_button=True,interactive=False)]+[gr.Textbox(visible=False)]*2
    
with gr.Blocks(title='Automatic Prompt Engineering', theme='soft', css="#textbox_id textarea {color: red}") as demo:
    gr.Markdown('# Automatic Prompt Engineering')

    original_prompt = gr.Textbox(label="请输入您的原始prompt", 
                                    lines=3)
    gr.Markdown('其中用户自定义变量使用{\{xxx\}}表示，例如{\{document\}}')
    with gr.Row():
        with gr.Column(scale=2):
            level = gr.Radio(['一次生成', '多次生成'], label="优化等级", value='一次生成')
            b1 = gr.Button("优化prompt")
        with gr.Column(scale=2):
            user_data = gr.Textbox(label="测试数据JSON", 
                                    lines=2)
            b2 = gr.Button("APE优化prompt")
    textboxes = []
    for i in range(3):
        t = gr.Textbox(label="我们为您生成的prompt", elem_id="textbox_id", lines=3,show_copy_button=True,interactive=False,visible=False if i>0 else True)
        textboxes.append(t)
    log = gr.Markdown('')
    b1.click(generate_prompt, inputs=[original_prompt, level], outputs=textboxes)
    b2.click(ape_prompt, inputs=[original_prompt, user_data], outputs=textboxes)
demo.launch()