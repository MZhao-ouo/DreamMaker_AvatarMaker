import gradio as gr
import time, io, requests, os
from PIL import Image, ImageDraw

base_img = Image.open("./imgs/base.png")
base_img = base_img.convert("RGBA")
base_img = base_img.resize((1080, 1080))

top_img = Image.open("./imgs/top.png")
top_img = top_img.convert("RGBA")
top_img = top_img.resize((1080, 1080))

def gen_avatar(image_path):
    if image_path is None:
        return gr.Image.update(value=None)
    imput_img = Image.open(image_path)
    imput_img = imput_img.convert("RGBA")
    imput_img = imput_img.resize((720, 720))
    # 把input_img裁剪成圆形
    mask = Image.new("L", imput_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + imput_img.size, fill=255)
    imput_img.putalpha(mask)

    mid_img = Image.new('RGBA', (1080, 1080), (0, 0, 0, 0))     # 创建一个新的透明图片
    # 计算非透明部分的位置
    left = (1080 - 720) // 2
    top = int(1080*8.7/100)
    mid_img.paste(imput_img, (left, top))       # 将imput_image放到img上
    mid_img = mid_img.resize((1080, 1080))      # 将图片转换成统一的尺寸
    result = Image.new("RGBA", base_img.size)       # 创建一个新的空白图像，尺寸和第一张图片相同
    # 把每张图片叠加到结果图片上
    result = Image.alpha_composite(result, base_img)
    result = Image.alpha_composite(result, mid_img)
    result = Image.alpha_composite(result, top_img)

    # 保存图片到result文件夹，文件名为当前时间戳
    timestamp = int(time.time())
    save_path = f"./result/{timestamp}.png"
    try:
        result.save(save_path)
        print("生成成功")
    except:
        print("保存图片失败")
     
    return result

def get_qq_avatar(qq_number):
    # 从url获取图片,返回一个pil图片
    url = f"https://q.qlogo.cn/headimg_dl?dst_uin={qq_number}&spec=640&img_type=jpg"
    r = requests.get(url)
    if r.status_code != 200:
        return gr.Image.update(value=None)
    qq_avatar = Image.open(io.BytesIO(r.content))
    return qq_avatar

def show_recent():
    imgs = []
    # 展示最近生成的头像
    imgs_path = os.listdir("./result")
    imgs_path.sort(reverse=True)
    imgs_path = imgs_path[:16]
    imgs_path = [f"./result/{img}" for img in imgs_path]
    return imgs_path

with open("assets/style.css", "r", encoding="utf-8") as f:
    customCSS = f.read()
with gr.Blocks(css=customCSS) as demo:
    # 居中大标题
    title = gr.HTML("<h1 style='text-align: center'>2023时光之书“造梦玩家”头像生成</h1><br>")
    
    with gr.Row():
        input_image = gr.Image(type="filepath", label="上传你的头像")
        output_image = gr.Image(interactive=False, label="生成的头像")
    qq_number = gr.Textbox(label="自动获取QQ头像", lines=1, placeholder="或者你也可以输入QQ号，一键生成")
    submit = gr.Button(label="自动获取qq头像")
    avatar_gallary = gr.Gallery(label="最近加入的造梦玩家").style(columns=8, rows=1, object_fit="contain", height="auto")

    demo.load(show_recent, [], [avatar_gallary])
    input_image.change(gen_avatar, [input_image], [output_image])
    submit.click(get_qq_avatar, [qq_number], [input_image])

if __name__ == "__main__":
    demo.queue(concurrency_count=99).launch(
        # favicon_path="./assets/favicon.ico",
        inbrowser=True, # 禁止在docker下开启inbrowser
    )
