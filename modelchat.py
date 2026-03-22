import request as r
import json as j
from config import *
import base64 as b
import io
from PIL import ImageGrab
import uiautomation as ui
def get_image():
    image=ImageGrab.grab()
    with io.BytesIO() as output:
        image.save(output,format="PNG")
        png_data=output.getvalue()
    base64data=b.b64encode(png_data).decode('utf-8')
    mimetype="image/png"
    return f"data:{mimetype};base64,{base64_data}"
def walk_ui_tree(control, depth=0):
    result = {
        "type": control.ControlTypeName,
        "name": control.Name,
        "class_name": control.ClassName,
        "automation_id": control.AutomationId,
        "bounds": [control.BoundingRectangle.left, 
                   control.BoundingRectangle.top,
                   control.BoundingRectangle.width(), 
                   control.BoundingRectangle.height()] if control.BoundingRectangle else None,
        "is_visible": control.IsVisible,
        "is_enabled": control.IsEnabled,
        "children": []
    }
    for child in control.GetChildren():
        result["children"].append(walk_ui_tree(child, depth + 1))
    return result
def image_introduce():
    durl=get_image()
    paylode={
            "model": IMAGE_MODEL["name"],
            "messages":[
                            {
                                "role": "user",
                                "content": [
                                {
                                "type": "text",
                                "text": '''You are given a screenshot of a computer screen. Your task is to analyze all visible GUI components and output a JSON tree that represents the hierarchical structure of these components.

The root node represents the entire screen. Its "category" must be "screen", and its "appearance" must be null. All other GUI elements (buttons, labels, input fields, checkboxes, icons, panels, etc.) should be nested under appropriate parent nodes based on their visual containment (e.g., a button inside a window is a child of that window).

For each node in the tree, provide the following fields:

- "category": The type of GUI component. Use one of the following common categories: "screen", "window", "panel", "button", "label", "text", "input", "checkbox", "radio", "dropdown", "icon", "image", "slider", "progress", "scrollbar", "menu", "dialog", "tooltip", or a reasonable custom category if none fits.  
  **Special case**: If a region contains no obvious standard controls (e.g., it is a game viewport, a photo viewer, or a custom-drawn area), set its category to "canvas" (or "unknown") instead.

- "appearance": An object describing the visual properties of the component. Include as many details as you can observe, such as:
  - "bounds": The bounding box in pixels relative to the screen, as [x, y, width, height] (where (0,0) is the top-left corner).
  - "background_color": The dominant background color (e.g., "#RRGGBB" or a CSS color name).
  - "text": The textual content displayed (if any).
  - "text_color": The color of any text (if applicable).
  - "font_size": Approximate font size in pixels.
  - "border": Whether a border is visible (boolean or description).
  - "rounded": Whether corners are rounded (boolean or approximate radius).
  - "state": If interactive, its state (e.g., "enabled", "disabled", "hovered", "pressed").
  - "icon_name" or "icon_description": If an icon, describe it.
  - If the category is "canvas", you must include a **"visual_description"** field inside "appearance" that narrates the visible content in detail. Describe all meaningful elements within that region, such as UI overlays (health bars, hunger meters, inventory slots) and world objects (blocks, creatures, items). Focus on visual appearance (colors, shapes, textures, counts, relative positions) rather than using proper nouns or game‑specific names. For example, instead of "sheep", say "a fluffy white four‑legged animal"; instead of "grass block", say "a green-topped cube with speckles". You may still use generic UI terms like "health bar" if they are clearly recognizable.
  - If a property is unclear or not applicable, you may omit it or set it to null.

- "children": An array of child nodes (if any). For leaf components (e.g., a single button), this can be an empty array or omitted.

The output must be **only a valid JSON object** (no additional text, markdown, or explanation). The JSON should be well-structured and properly indented for readability.

Here are two examples to illustrate the expected format:

**Example 1: Standard GUI application**
{
  "category": "screen",
  "appearance": null,
  "children": [
    {
      "category": "window",
      "appearance": {
        "bounds": [100, 50, 600, 400],
        "background_color": "#F0F0F0",
        "title": "Settings"
      },
      "children": [
        {
          "category": "label",
          "appearance": {
            "text": "Volume:",
            "bounds": [120, 100, 80, 20],
            "text_color": "#000000",
            "font_size": 12
          }
        },
        {
          "category": "slider",
          "appearance": {
            "bounds": [210, 100, 200, 20],
            "background_color": "#CCCCCC",
            "value": 70
          }
        },
        {
          "category": "button",
          "appearance": {
            "text": "OK",
            "bounds": [400, 350, 80, 30],
            "background_color": "#0078D7",
            "text_color": "#FFFFFF",
            "rounded": true
          }
        }
      ]
    },
    {
      "category": "icon",
      "appearance": {
        "bounds": [20, 20, 48, 48],
        "icon_description": "Recycle Bin",
        "background_color": "transparent"
      }
    }
  ]
}

**Example 2: Game screen with canvas region**
{
  "category": "screen",
  "appearance": null,
  "children": [
    {
      "category": "canvas",
      "appearance": {
        "bounds": [0, 0, 1920, 1080],
        "background_color": "#87CEEB",
        "visual_description": "The main game view shows a grassy field with scattered trees. In the top‑left corner, there is a row of ten red hearts (all full) representing health, and next to them ten drumstick icons (nine full, one empty) for hunger. At the bottom center, a hotbar with nine slots contains various blocks: a green‑topped cube, a gray cobblestone‑textured cube, a wooden‑plank cube, a pickaxe, a sword, etc. The player's hand is visible holding a sword. In the distance, a few white fluffy four‑legged animals (sheep‑like) and a tall green plant (cactus) are visible."
      },
      "children": []   // No nested standard controls, but the canvas itself is described in detail.
    }
  ]
}

Please analyze the screenshot carefully and generate a comprehensive JSON tree for all visible GUI components. Include as much detail as possible in the "appearance" objects. If you are uncertain about a specific value, make a reasonable guess based on visual cues.'''
                                },
                                {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_data_uri                                }
                            }
                        ]
                    }
                ]
        }
    headers = {
        "Authorization": f"Bearer {IMAGE_MODEL['key']}",
        "Content-Type": "application/json"
    }
    response=r.post(IMAGE_MODEL["api"],headers=headers,json=paylode)
    if response.status_code==200:
        result=response.json()
        reply = result["choices"][0]["message"]["content"]
        return reply
    else:
        return "The image recognition model failed to return results, so you can only query the UI tree."
def get_command(task,mx,my):
    vj=image_introduce()
    desktop=ui.GetRootControl()
    ui_tree=walk_ui_tree(desktop)
    ui_tree=j.dumps(ui_tree,indent=2,sort_keys=False,ensure_ascii=False)
    p=f'''You are a screen operation assistant. You will receive:
- Visual description of the screen (JSON) : {{vision_json}}
- UI control tree of the screen (JSON) : {{ui_json}}
- Current mouse coordinates : {{mouse_x}}, {{mouse_y}}
- User task : {{user_task}}

Your goal is to analyze the screen content, understand the user's task, and generate a sequence of operations (mouse and keyboard events) to accomplish it. Return a JSON object with the following structure:

{
  "target_window": "<window_title_or_desktop>",
  "command": [
    {
      "action": "<action_type>",
      "args": { <parameters> }
    },
    ...
  ]
}

The target_window should be the exact window title (as seen in the UI tree or visual description) where the main interaction occurs. If the task involves multiple windows, choose the primary one. Use "desktop" for global actions like clicking desktop icons. The execution system will attempt to bring that window to the foreground before performing the commands.

Supported action types and their parameters:

**Mouse actions (coordinates are screen absolute pixels):**
- "click": Left button click.
  Args: {"pos": [x, y], "button": "left"|"right"|"middle", "clicks": 1|2}
  "button" defaults to "left", "clicks" defaults to 1 (single click). Use clicks=2 for double-click.
- "long_press": Press and hold left button.
  Args: {"pos": [x, y], "length": milliseconds, "button": "left"|"right"|"middle"}
  "button" defaults to "left".
- "drag": Drag mouse (press left, move, release).
  Args: {"start_pos": [x1, y1], "end_pos": [x2, y2], "length": milliseconds, "shake": float 0.0~1.0, "button": "left"|"right"|"middle"}
  "length" is total drag duration; default 500. "shake" simulates human jitter: 0=perfectly straight, 1=max random. Default 0.2. "button" defaults to "left".
- "move": Move mouse without pressing.
  Args: {"end_pos": [x, y], "duration": seconds}
  "duration" is movement time; default 0 (instant).
- "scroll": Scroll mouse wheel.
  Args: {"amount": integer, "x": optional, "y": optional}
  Positive amount scrolls up, negative down. Typically 120 is one notch. If x and y are provided, mouse moves there before scrolling.

**Keyboard actions:**
- "key_press": Press and release a key (or combination).
  Args: {"key": "character", "modifiers": ["ctrl","alt","shift","win"]}
  "key" can be a single character (e.g., "a") or special key name: "enter","space","tab","backspace","delete","esc","up","down","left","right","home","end","pageup","pagedown","f1"..."f12", etc. "modifiers" is optional list of modifier keys.
- "key_down": Press and hold a key (with optional modifiers).
  Args: same as key_press.
- "key_up": Release a key (with optional modifiers).
  Args: same as key_press.

**Special commands:**
- "output": Send a message to the user.
  Args: {"txt": "string"}
- "endtask": End the current task.
  Args: {} (empty object)

Important notes:
- Coordinates: All mouse positions must be screen absolute coordinates. Use UI tree bounds (which are usually screen coordinates) to compute center: [left + width/2, top + height/2] (rounded to int). If a control is described only visually, infer coordinates from the visual description.
- Priority: Prefer UI tree positions if the control exists and is visible; otherwise rely on visual description.
- Window activation: The system will attempt to activate target_window before the command sequence. If the window cannot be found, the commands may be sent to the currently active window. If the window is minimized, it will be restored automatically.
- Task planning: Consider current screen state (e.g., whether the needed window is already open). If the window is not present, you may include steps to open it first (e.g., using Win key + typing the application name). The command list should be sequential.
- If the task cannot be completed (e.g., required control not found), return {"target_window":"desktop","command":[]} and optionally an output message explaining why.
- Return ONLY the JSON object. No extra text, explanations, or markdown.

Example input (partial):
- Visual description: {"category":"screen","children":[{"category":"window","appearance":{"bounds":[100,50,600,400],"title":"Calculator"},"children":[{"category":"button","appearance":{"text":"7","bounds":[120,100,50,50]}}]}]}
- UI tree: {"type":"Desktop","children":[{"type":"Window","name":"Calculator","bounds":[100,50,600,400],"children":[{"type":"Button","name":"7","bounds":[120,100,50,50]}]}]}
- Current mouse: [500,300]
- User task: "Click the 7 button on the calculator"

Output:
{
  "target_window": "Calculator",
  "command": [
    {"action": "move", "args": {"end_pos": [145, 125]}},
    {"action": "click", "args": {"pos": [145, 125], "button": "left"}}
  ]
}
(Button center: 120+25=145, 100+25=125.)

Now process the actual inputs:
Visual description: {{vision_json}}
UI tree: {{ui_json}}
Current mouse: {{mouse_x}}, {{mouse_y}}
User task: {{user_task}}

Output JSON:

'''
    headers = {
        "Authorization": f"Bearer {TEXT_MODEL['key']}",
        "Content-Type": "application/json"
    }
    data = {
        "model": TEXT_MODEL["name"],
        "messages": [
            {"role": "user", "content": p}
        ],
        "temperature": 0.7
    }
    response=r.post(TEXT_MODEL["api"],headers=headers,json=data)
    if response.status_code==200:
        result = response.json()
        reply = result["choices"][0]["message"]["content"]
        return reply
    else:
        return response.status_code
