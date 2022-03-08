# Image Manipulation

import io

import discord
from PIL import Image, ImageDraw, ImageFont, ImageOps

calc_xp = lambda l: 250 * 1.5 ** (l - 1)


def draw_rank(level: int, xp: int, rank: int, sold: int, maxed: bool, member: discord.Member, avatar):
    im = Image.open(io.BytesIO(avatar)).convert("RGBA")
    im = im.resize((150, 150))

    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    im.putalpha(mask)

    output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    output.save('media/output/output.png')

    custom_bk = False

    if member.display_name == "ZenoX" or member.name == "ZenoX":
        background = Image.open('media/universe-background.png').convert("RGBA")
        custom_bk = True
    elif member.display_name == "Erdis" or member.name == "Erdis":
        background = Image.open('media/poly-background.png').convert("RGBA")
        custom_bk = True
    else:
        background = Image.open('media/background.png').convert("RGBA")

    fontsize = round(38 - len(member.display_name) / 2) if len(member.display_name) / 2 > 0 else 38

    font1 = ImageFont.truetype('media/PTSansCaption-Bold.ttf', 38)
    font2 = ImageFont.truetype('media/PTSansCaption-Bold.ttf', 48)
    font3 = ImageFont.truetype('media/Comfortaa-SemiBold.ttf', fontsize)
    font4 = ImageFont.truetype('media/Oswald-Medium.ttf', 25)

    draw = ImageDraw.Draw(background, "RGBA")

    # Colors!
    label_color = (255, 255, 255)
    var_color = (0, 146, 255)
    bar_bk_color = (100, 100, 100)
    trans_bar_bk_color = (200, 200, 200, 150)
    bar_color = (114, 137, 218)

    max_color = (197, 144, 53)  # gold
    max_color_trans = (197, 144, 53, 100)

    levelpos = 890
    levelpos1 = levelpos - (27 * len(str(round(level))) + 10)
    rankpos = levelpos1 - 68
    rankpos1 = rankpos - (27 * len(str(rank)) + 40)
    soldpos = rankpos1 - 68
    soldpos1 = soldpos - (22 * len(str(sold)) + 45)

    percent = xp / calc_xp(level)

    xpoffset = 600 * percent

    total_xp = round(calc_xp(level))

    # IF the user has a rate over the guild's maximum:
    if maxed:
        draw.text(xy=(575, 189), text=f"MAXED", fill=(255, 255, 255), anchor="mt", font=font1)

        # Set certain colors to gold
        var_color = max_color
        bar_color = max_color
        trans_bar_bk_color = max_color_trans

    # Semi-Transparent Overlay
    if custom_bk:
        overlay = Image.new("RGBA", background.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay, "RGBA")

        # Semi-Transparent background for XP bar
        overlay_draw.rectangle([275, 184, 275 + 600, 220], fill=trans_bar_bk_color)
        overlay_draw.ellipse([255, 184, 290, 220], fill=trans_bar_bk_color)
        overlay_draw.ellipse([255 + 600, 184, 290 + 600, 220], fill=trans_bar_bk_color)
        background.paste(Image.alpha_composite(background, overlay))
    else:
        draw.rectangle([275, 184, 275 + 600, 220], fill=bar_bk_color)
        draw.ellipse([255, 184, 290, 220], fill=bar_bk_color)
        draw.ellipse([255 + 600, 184, 290 + 600, 220], fill=bar_bk_color)



    draw.text(xy=(levelpos, 92), text=f"{level}", fill=var_color, anchor="rb", font=font2)
    draw.text(xy=(levelpos1, 90), text=f"LEVEL", fill=label_color, anchor="rb", font=font4)
    draw.text(xy=(rankpos, 92), text=f"#{rank}", fill=var_color, anchor="rb", font=font2)
    draw.text(xy=(rankpos1, 90), text=f"RANK", fill=label_color, anchor="rb", font=font4)
    draw.text(xy=(soldpos, 92), text=f"{sold}M", fill=var_color, anchor="rb", font=font1)
    draw.text(xy=(soldpos1, 90), text=f"SOLD", fill=label_color, anchor="rb", font=font4)
    draw.text(xy=(850 - (75 + 21 * len(str(round(calc_xp(level))))), 125), text=f"{round(xp)}",
               fill=var_color, anchor="ra", font=font1)
    draw.text(xy=(875, 125), text=f"/ {total_xp} XP", fill=label_color, anchor="ra",
               font=font1)
    draw.text(xy=(270, 165), text=f"{member.display_name[:20]}", fill=(255, 255, 255), anchor="lb", font=font3)


    # XP Bar
    draw.rectangle([275, 184, 275 + xpoffset, 220], fill=bar_color)
    draw.ellipse([255, 184, 290, 220], fill=bar_color)
    draw.ellipse([255 + xpoffset, 184, 290 + xpoffset, 220], fill=bar_color)

    # User Avatar
    background.paste(output, (80, 66), output)

    # background.paste(template, (0, 0), template)
    final_buffer = io.BytesIO()
    background.save(final_buffer, 'png')
    final_buffer.seek(0)

    return final_buffer
