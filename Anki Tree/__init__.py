from aqt import mw, gui_hooks
from aqt.deckbrowser import DeckBrowser

from . import cards, overlay

mw.addonManager.setWebExports(__name__, r"web/.*\.(js|css)")


def inject_tree_assets(web_content, context):
    if not isinstance(context, DeckBrowser):
        return
    addon = mw.addonManager.addonFromModule(__name__)
    web_content.js.append(f"/_addons/{addon}/web/tree.js")



gui_hooks.deck_browser_did_render.append(overlay.on_deck_browser_render)
gui_hooks.webview_did_receive_js_message.append(overlay.on_js_message)
gui_hooks.webview_will_set_content.append(inject_tree_assets)
gui_hooks.main_window_did_init.append(overlay.create_overlay)
gui_hooks.state_did_change.append(overlay.on_state_change)
