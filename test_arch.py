"""
SDG3 Educational Simulation Game - NiceGUI Implementation
Main application entry point
Phase 1 Complete: Start code, region tags, session state fixed
"""
from nicegui import ui, app
import database as db
import game_plot_ug
import ugregmod
from files import luf_original
from tb2_claude import get_tab, get_inv_props

app.add_static_files('/static', 'static')

async def detect_browser_settings():
    """Detect user's browser language and color scheme preference"""
    
    # Detect language
    lang_code = await ui.run_javascript('''
        navigator.language || navigator.userLanguage || 'en'
    ''')
 
    # Map browser language code to your language system
    # e.g., 'en-US' -> 'en', 'de-DE' -> 'de'
    lang = lang_code.split('-')[0] if lang_code else 'en'
    
    # Map to your langx index
    lang_map = {'en': 0, 'de': 1, 'fr': 3, 'no': 4}  # Add your languages
    langx = lang_map.get(lang, 0)  # Default to 0 (English)
    
    return lang, langx

def set_mode_btn(d):
    is_dark = app.storage.tab.get('dark_mode')
    if not is_dark:
        app.storage.tab['dark_mode'] = True
        ui.dark_mode().enable()
    else:
        app.storage.tab['dark_mode'] = False
        ui.dark_mode().disable()
    ui.navigate.reload()
    

# Initialize dark mode from storage (call this on each page)
async def init_dark_mode():
    await ui.context.client.connected()
    if 'dark_mode' in app.storage.tab:
        if app.storage.tab['dark_mode']:
            ui.dark_mode().enable()
        else:
            ui.dark_mode().disable()
        return app.storage.tab['dark_mode']
    else:
        # Default to False (light mode)
        app.storage.tab['dark_mode'] = False
        ui.dark_mode().disable()
        return False

# Reusable theme toggle button
def create_theme_toggle_button():
    """Create and return a theme toggle button with proper icon and behavior"""
    current_mode = app.storage.tab.get('dark_mode', False)
    btn_icon = 'nightlight' if not current_mode else 'light_mode'
    theme_btn = ui.button(icon=btn_icon).props('flat round dense').classes('text-yellow bg-orange-700')

    def toggle_theme():
        current_mode_dark = app.storage.tab.get('dark_mode')
        new_mode = False if current_mode_dark else True
        # Update button icon
        set_mode_btn(new_mode)
        theme_btn.props(f'icon={"nightlight" if not new_mode else "light_mode"}')
    
    theme_btn.on_click(toggle_theme)

    return theme_btn

async def create_header():
    """Create persistent header with language and theme controls"""
    await ui.context.client.connected()
    ui.colors(primary='#014873', secondary='#0383a1', accent='#9C27B0')    
    with ui.header().classes('items-center justify-between px-2 py-3'):
        # Left side - App title
        with ui.link(target='/'):
            with ui.column().classes('gap-0 text-white font-bold'):
                ui.label('SimFuture').classes('text-2xl')
                ui.label('The Age of Consequences').classes('font-italic')
        
        # Right side - Controls
        with ui.row().classes('gap-2 items-center'):
            # Help button - opens external page
            langx = app.storage.tab.get('langx', 0)
            if langx == 0:
                help_link = 'https://www.manula.com/manuals/blue-way/sdg-game/01/uk/topic/sinn-und-zweck'
            elif langx == 1 or langx == 2:
                help_link = 'https://www.manula.com/manuals/blue-way/sdg-game/01/de/topic/sinn-und-zweck'
            else:
                help_link = 'https://www.manula.com/manuals/blue-way/sdg-game/01/uk/topic/sinn-und-zweck'

            with ui.button(icon='blind',
                on_click=lambda: ui.navigate.to(help_link, new_tab=True)
                        ).props('flat round dense').classes('text-white font-bold'):
                ui.tooltip(luf_original.help_tip[langx]).classes('bg-green-300 text-black')

            with ui.button(icon='gavel',
                on_click=lambda: ui.navigate.to('/legal')
                        ).props('flat round dense').classes('text-white font-bold'):
                ui.tooltip(luf_original.legal[langx]).classes('bg-green-300 text-black')
                            
            with ui.button(icon='claude',
                on_click=lambda: ui.navigate.to('https://claude.ai/login', new_tab=True)
                        ).props('flat round dense icon=img:/static/claudeAI.png').classes('text-white font-bold'):
                ui.tooltip(luf_original.claude[langx]).classes('bg-green-300 text-black')
                            
           # Language selector
            lang_options = {
                'en': '🇬🇧 English',
                'de': '🇩🇪 Deutsch',
                'fr': '🇫🇷 Français',
                'no': '🇳🇴 Norsk'
            }
            
            current_lang = app.storage.tab.get('lang', 'en')
            
            lang_select = ui.select(
                options=lang_options,
                value=current_lang,
                label='Language'
            ).classes('w-30').props('dense outlined dark')
            
            def change_language():
                new_lang = lang_select.value
                lang_map = {'en': 0, 'de': 1, 'fr': 3, 'no': 4}
                langx = lang_map.get(new_lang, 0)
                
                app.storage.tab['lang'] = new_lang
                app.storage.tab['langx'] = langx
                
                username = app.storage.tab.get('username')
                if username:
                    db.save_player_preferences(
                        username, 
                        new_lang, 
                        langx
                    )

                ui.notify(f'{lang_options[new_lang]}')
                ui.navigate.reload()
            
            lang_select.on('update:model-value', change_language)
            
            create_theme_toggle_button()


def show_still_missing(lang: str, langx: int, game_id: str, current_round: int, region_tag: str):
    """Show dialog with list of all players still missing in a region"""
    still_missing = db.get_logged_for_reg(game_id, current_round, region_tag)
    if len(still_missing) == 0:
#        ui.notify('in show_still_missing  == 0')
        return False
    
    minis = luf_original.mini_to_long[langx]
    with ui.dialog() as dialog, ui.card().classes('w-full max-w-2xl'):
        ui.label(luf_original.still_not_logged_in_to_this_round[langx]).classes('text-2xl font-bold mb-4')
        
        # Create table
        with ui.card().classes('w-full p-0'):
            columns = [
                {'name': 'ministry', 'label': luf_original.ministries_upper[langx], 'field': 'ministry'},
            ]
            
            rows = []
            for player in still_missing:
                rows.append({
                    'ministry': minis[player],
                })
            
            ui.table(columns=columns,
                     rows=rows,
                     row_key='ministry',
                     column_defaults={'align': 'left'}).props('dense separator="none"').classes('w-full')
        ui.button(luf_original.close[langx], on_click=dialog.close).classes('w-full mt-4')
    
    dialog.open()

            

# ============================================================================
# ENTRY PAGE
# ============================================================================

@ui.page('/')
async def entry_page():
    """Main entry page - start/continue game or join game"""
     # Detect browser settings on first visit
    await ui.context.client.connected()
    if app.storage.tab.get('lang') is None:
        lang, langx = await detect_browser_settings()
        app.storage.tab['lang'] = lang
        app.storage.tab['langx'] = langx
    
    ui.colors(primary='#014873', secondary='#0383a1', accent='#9C27B0')
    
    # Add header
    await ui.context.client.connected()
    init_dark_mode()
    create_header()
    
    # Main content
    with ui.column().classes('w-full max-w-2xl mx-auto p-8 gap-6'):
        ui.markdown(luf_original.sdg_first_page[app.storage.tab['langx']]).classes('w-full text-3xl font-bold text-center')
        ui.button(luf_original.about_btn_tx[app.storage.tab['langx']], icon='about',
                  on_click=lambda: ui.navigate.to('/about'), color='#FF8F2E').classes('w-full text-black font-bold')

        ui.separator()
        
        # GM Section
        with ui.card().classes('w-full p-6'):
            ui.label(luf_original.game_master[app.storage.tab['langx']]).classes('text-2xl font-bold mb-4')
            
            with ui.row().classes('w-full gap-4'):
                ui.button(luf_original.start_new_game[app.storage.tab['langx']], 
                         on_click=lambda: ui.navigate.to('/gm/new'),
                         icon='add_circle').classes('flex-1')
                
                ui.button(luf_original.continue_existing_game[app.storage.tab['langx']], 
                         on_click=lambda: ui.navigate.to('/gm/continue'),
                         icon='play_arrow').classes('flex-1')
        
        # Player Section
        with ui.card().classes('w-full p-6'):
            ui.label(luf_original.IamaPlayer[app.storage.tab['langx']]).classes('text-2xl font-bold mb-4')
            
            with ui.row().classes('w-full gap-4'):
                ui.button(luf_original.joining[app.storage.tab['langx']], 
                         on_click=lambda: ui.navigate.to('/player/join'),
                         icon='person_add', color='secondary').classes('flex-1')
                
                ui.button(luf_original.rejoining[app.storage.tab['langx']], 
                         on_click=lambda: ui.navigate.to('/player/resume'),
                         icon='login', color='secondary').classes('flex-1')


# ============================================================================
# GM - START NEW GAME
# ============================================================================

@ui.page('/gm/new')
def gm_new_game():
    init_dark_mode()
    create_header()
    """GM starts a new game - requires start code 'oscar'"""

    
    with ui.column().classes('w-full max-w-2xl mx-auto p-8 gap-6'):
        ui.label(luf_original.start_new_game[app.storage.tab['langx']]).classes('text-3xl font-bold')
        
        with ui.card().classes('w-full p-6'):
            start_code_input = ui.input(luf_original.enter_code_title_tx[app.storage.tab['langx']],
                                       placeholder=luf_original.enter_code_tx[app.storage.tab['langx']],
                                       password=True,
                                       password_toggle_button=True).props('autofocus').on('keydown.enter', lambda: create_game()).classes('w-full').classes('text-blue-600 dark:text-orange-500')

            username_input = ui.input(luf_original.your_username_game_master[app.storage.tab['langx']],
                                     placeholder=luf_original.please_enter_a_username[app.storage.tab['langx']]).on('keydown.enter', lambda: create_game()).classes('w-full')
            
            error_label = ui.label('').classes('text-red-500')
            
            def create_game():
                start_code = start_code_input.value.strip()
                username = username_input.value.strip()
                
                # Validate start code first
                if start_code != db.START_CODE:
                    error_label.text = luf_original.wrong_code_tx[app.storage.tab['langx']]
                    return
                
                if not username:
                    error_label.text = luf_original.please_enter_a_username[app.storage.tab['langx']]
                    return
                
                # Check if username is available globally (including as GM)
                player_info = db.get_player_info(username)
                if player_info:
                    error_label.text = luf_original.username_already_taken_please_choose_another[app.storage.tab['langx']]
                    return
                
                # Check if username is already a GM
                with db.get_db() as conn:
                    cursor = conn.execute("SELECT game_id FROM games WHERE gm_username = ?", (username,))
                    if cursor.fetchone():
                        error_label.text = luf_original.username_already_taken_as_gm_please_choose_another[app.storage.tab['langx']]
                        return
                
                # Create game (always 3 rounds)
                game_id = db.create_game(username)
                
                # Update session
                app.storage.tab['username'] = username
                app.storage.tab['game_id'] = game_id
                app.storage.tab['role'] = 'gm'
                
                ui.navigate.to(f'/gm/config')
            
            ui.button(luf_original.create_game[app.storage.tab['langx']], on_click=create_game, icon='create').classes('w-full')
        
        ui.button(luf_original.btn_back[app.storage.tab['langx']], on_click=lambda: ui.navigate.to('/'), 
                 icon='arrow_back').classes('mt-4')


# ============================================================================
# GM - CONTINUE EXISTING GAME
# ============================================================================

@ui.page('/gm/continue')
def gm_continue_game():
    """GM continues existing game - only asks for username"""
    init_dark_mode()
    create_header()
    
    with ui.column().classes('w-full max-w-2xl mx-auto p-8 gap-6'):
        ui.label('Continue Existing Game').classes('text-3xl font-bold')
        
        with ui.card().classes('w-full p-6'):
            ui.label('Enter your Game Master username to restore your game').classes('mb-4')
            
            username_input = ui.input('Your Username',
                                     placeholder='Enter your GM username').props('autofocus').on('keydown.enter', lambda: check_and_continue()).classes('w-full')
            
            error_label = ui.label('').classes('text-red-500')
            game_info_label = ui.label('').classes('text-orange-600')
            
            def check_and_continue():
                username = username_input.value.strip()
                
                if not username:
                    error_label.text = 'Please enter your username'
                    game_info_label.text = ''
                    return
                
                # Look up game by GM username (GMs are in games table, not players table)
                with db.get_db() as conn:
                    cursor = conn.execute(
                        """
                        SELECT game_id, num_rounds, current_round, state
                        FROM games 
                        WHERE gm_username = ?
                        ORDER BY created_at DESC
                        LIMIT 1
                        """,
                        (username,)
                    )
                    game = cursor.fetchone()
                
                if not game:
                    error_label.text = 'No game found for this username'
                    game_info_label.text = ''
                    return
                
                # Found game - show info
                error_label.text = ''
                game_id = game['game_id']
                game_info_label.text = f"Game found: {game_id} | Rounds: {game['num_rounds']} | Current: {game['current_round']} | State: {game['state']}"
                
                # Update session
                app.storage.tab['username'] = username
                app.storage.tab['game_id'] = game_id
                app.storage.tab['role'] = 'gm'
                
                # Navigate to GM config/dashboard
                ui.navigate.to('/gm/config')
            
            ui.button('Continue Game', on_click=check_and_continue, 
                     icon='play_arrow').classes('w-full mt-4')
        
        ui.button('← Back', on_click=lambda: ui.navigate.to('/'), 
                 icon='arrow_back').classes('mt-4')


# ============================================================================
# GM - CONFIGURATION PAGE --- ORIGINAL
# ============================================================================
@ui.page('/gm/config')
def gm_config_page():
    """GM configuration page - shows game info and AI region selection"""
    init_dark_mode()
    create_header()
    
    if not app.storage.tab.get('game_id') or app.storage.tab.get('role') != 'gm':
        ui.navigate.to('/')
        return
    
    game_id = app.storage.tab['game_id']
    username = app.storage.tab['username']
    langx = app.storage.tab['langx']
    lang = app.storage.tab['lang']
    
    # Get game info
    game_info = db.get_game_info(game_id)
    current_round = game_info['current_round']
    
    with ui.column().classes('w-full max-w-4xl mx-auto p-8 gap-6'):
        ui.label(luf_original.game_master[langx]+': '+username).classes('text-3xl font-bold')
        ui.label(luf_original.gm_id_title_str[langx]+ ': ' + game_id).classes('text-2xl text-orange-600 font-mono')
        
        ui.separator()
        
        # Show AI regions
        ai_regions = db.get_ai_regions(game_id)
        regis = luf_original.regs[lang]
        if ai_regions:
            with ui.card().classes('w-full p-4 bg-blue-50'):
                ui.label(luf_original.ai_controlled_regions[langx]).classes('text-xl font-bold mb-2')
                for region_tag in sorted(ai_regions):
                    display_name = regis[region_tag]
                    ui.label(f'{display_name}').classes('text-base text-orange-700')
        
        
       # AI Region Selection (only if round 0)
        if current_round == 0:
            with ui.card().classes('w-full p-6'):
                ui.label(luf_original.check_regions_NOT_played_by_students_participants[langx]).classes('text-2xl font-bold mb-4')
                
                # Get current AI regions
                current_ai_regions = db.get_ai_regions(game_id)
                
                # Create checkboxes for each region
                ai_checkboxes = {}
                
                with ui.column().classes('w-full gap-2'):
                    for region_tag, display_name in sorted(regis.items(), key=lambda x: x[1]):
                        ai_checkboxes[region_tag] = ui.checkbox(
                            display_name,
                            value=(region_tag in current_ai_regions)
                        ).classes('text-base')
                
                status_label = ui.label('').classes('mt-4')
                
                def save_ai_regions():

                    try:
                        # Get selected AI regions
                        selected_ai = [tag for tag, checkbox in ai_checkboxes.items() if checkbox.value]
                        
                        # Validate: at least 1 region must be human-playable
                        if len(selected_ai) >= 10:
                            status_label.text = luf_original.at_least_1_region_must_be_played_by_humans[langx]
                            status_label.classes('text-red-600')
                            return
                        
                        # Save to database
                        db.set_ai_regions(game_id, selected_ai)                        

                        # USE ONE CONNECTION FOR EVERYTHING
                        spinner = ui.spinner('dots', size='xl', color='red')
                        with db.get_db() as conn:
                            # First, delete any existing AI players for this game
                            conn.execute(
                                "DELETE FROM players WHERE game_id = ? AND is_ai = 1",
                                (game_id,)
                            )
                            player_count = 0
                            created_usernames = set()  # Track what we've created
                            
                            for ai_region_tag in selected_ai:
                                for ministry in db.MINISTRIES:
                                    # Make username globally unique by including game_id
                                    ai_username = f"AI_{game_id}_{ai_region_tag}_{ministry}"
                                    
                                    # Check for duplicate before inserting
                                    if ai_username in created_usernames:
                                        print(f"⚠️  DUPLICATE DETECTED: {ai_username}")
                                        continue
                                    
                                    created_usernames.add(ai_username)
                                    
                                    conn.execute(
                                        """
                                        INSERT INTO players (username, game_id, region_tag, ministry, is_ai)
                                        VALUES (?, ?, ?, ?, ?)
                                        """,
                                        (ai_username, game_id, ai_region_tag, ministry, True)
                                    )
                                    player_count += 1                                    
                            
                            conn.commit()
                            print(f"✅ Created {player_count} AI players")

                            # Verify immediately on same connection
                            cursor = conn.execute(
                                "SELECT COUNT(*) as count FROM players WHERE game_id = ? AND is_ai = 1",
                                (game_id,)
                            )
                            count = cursor.fetchone()['count']
                            print(f"🔍 Verified: {count} AI players in database")
                        
                        # Now generate policies (in its own connection, after commit)
                        db.generate_ai_policy_decisions(game_id)
                        spinner.delete()
                                                                        
                        # Advance to Round 1
                        with db.get_db() as conn:
                            conn.execute(
                                """
                                UPDATE games
                                SET current_round = 1, state = 'playing', updated_at = CURRENT_TIMESTAMP
                                WHERE game_id = ?
                                """,
                                (game_id,)
                            )
                            conn.commit()
                        
                        print(f"✅ Game advanced to round 1")
                        status_label.text = luf_original.ai_regions_saved_and_round_1_started[langx]
                        status_label.classes('text-green-600')
                        ui.navigate.to(f'/gm/board?game_id={game_id}')
                        
                    except Exception as e:
                        print(f"❌ ERROR: {e}")
                        import traceback
                        traceback.print_exc()
                        status_label.text = luf_original.x_error[langx]+str(e)
                        status_label.classes('text-red-600')                    
                                    
                
                ui.button(luf_original.save_ai_region_selection_start_game[langx], 
                         on_click=save_ai_regions, 
                         icon='play_arrow').classes('w-full mt-4')
        else:
            # Game already started
            ui.button(luf_original.go_to_game_board[langx],
                     on_click=lambda: ui.navigate.to(f'/gm/board?game_id={game_id}'),
                     icon='dashboard').classes('w-full mt-4')
        
        ui.button(luf_original.back_to_home[langx], on_click=lambda: ui.navigate.to('/'), 
                 icon='home').classes('mt-4')


# ============================================================================
# GM - GAME BOARD
# ============================================================================

@ui.page('/gm/board')
def gm_game_board(game_id: str = None):
    """GM game board - pre-built card architecture"""

    init_dark_mode()
    create_header()

    # Auth: accept game_id from URL param (post-model-run) OR from session (normal)
    if game_id:
        gm_info = db.get_game_info(game_id)
        print('ln 542 (gm_info):', end=' ')
        print(gm_info)
        if not db.get_game_info(game_id):
            ui.navigate.to('/')
            return
    else:
        if not app.storage.tab.get('game_id') or app.storage.tab.get('role') != 'gm':
            ui.navigate.to('/')
            return
        game_id = app.storage.tab['game_id']

    username = app.storage.tab.get('username', 'GM')
    langx = app.storage.tab.get('langx', 0)
    lang = app.storage.tab.get('lang', 'en')
    regis = luf_original.regs[lang]

    # Get game info
    game_info = db.get_game_info(game_id)
    current_round = game_info['current_round']
    num_rounds = game_info['num_rounds']
    game_state = game_info['state']

    # Initial state queries
    not_logged_in_init = db.get_logged(game_id, current_round)
    unsubmitted_init = db.get_unsubmitted_regions(game_id, current_round)
    all_logged_init = len(not_logged_in_init) == 0
    all_submitted_init = len(unsubmitted_init) == 0

    with ui.column().classes('w-full max-w-6xl mx-auto p-8 gap-6'):
        # ── Header ────────────────────────────────────────────────────────
        with ui.row().classes('w-full items-center justify-between'):
            with ui.column():
                ui.label(luf_original.msg_gm_board_head_str[langx]).classes('text-3xl font-bold')
                ui.label(luf_original.game[langx]+' '+game_id+' | '+luf_original.runde[langx]+': '+str(current_round)+'/'+str(num_rounds)).classes('text-xl text-orange-600 font-mono')

            ui.button(luf_original.gmau_btn_tx[langx],
                     on_click=lambda: show_player_ids_dialog(game_id, lang, langx),
                     icon='people').classes('text-lg')

        ui.separator()

        # ── Card 1: Instructions (always visible) ─────────────────────────
        with ui.card().classes('w-full p-4 bg-amber-50') as card_instructions:
            with ui.column():
                ui_gm_lab = ui.label(luf_original.ui_gm_lab_start[langx]).classes('text-2xl text-primary font-bold mb-4')
                if current_round == 1:
                    ui_gm_info = ui.markdown(luf_original.ui_gm_info_start[langx]).classes('text-base mb-2 text-orange-800')
                else:
                    ui.label(f'Round {current_round} is in progress.').classes('text-base mb-2 text-orange-800')
                    ui.label('Monitor player submissions below. When all have submitted, you can advance to the next round.').classes('text-base mb-4 text-orange-800')

        # ── Card 2: Not logged in (who is still missing?) ─────────────────
        with ui.card().classes('w-full p-4 bg-red-100') as card_not_logged_in:
            with ui.column().classes('w-full'):
                ui.label(
                    luf_original.submission_status_for_round[langx]+str(current_round)+luf_original.ask_if_they_need_help[langx]
                ).classes('text-lg text-primary font-bold mb-2')
                login_table_container = ui.column().classes('w-full')
        card_not_logged_in.set_visibility(not all_logged_init)

        # ── Card 3: Allow / prevent submissions ───────────────────────────
        with ui.card().classes('w-full p-4 bg-amber-100') as card_allow_prevent:
            with ui.column().classes('w-full'):
                ui.label(luf_original.submission_control[langx]).classes('text-lg font-bold mb-2 text-primary')
                are_open_init = db.get_accept_decisions(game_id, current_round)

                def on_accept_toggle():
                    new_val = 1 if accept_switch.value else 0
#                    db.set_accept_decisions(game_id, current_round, new_val)
                    ui.notify(game_id + ' ' + str(new_val))
                    db.set_accept_decisions(game_id, current_round, new_val)
                    accept_switch.text = luf_original.yes_submissions_allowed[langx] if accept_switch.value else luf_original.no_submissions_not_allowed[langx]

                accept_switch = ui.switch(
                    luf_original.yes_submissions_allowed[langx] if are_open_init == 1 else luf_original.no_submissions_not_allowed[langx],
                    value=are_open_init == 1,
                    on_change=lambda: on_accept_toggle()
                ).classes('font-bold')
        card_allow_prevent.set_visibility(all_logged_init and not all_submitted_init)

        # ── Card 4: Advance to next round ─────────────────────────────────
        with ui.card().classes('w-full p-4 bg-amber-200') as card_advance:
            with ui.column():
                ui.label('✓ All regions have submitted!').classes('text-xl font-bold text-secondary mb-2')
                ui.label(f'Ready to advance to Round {current_round + 1}?').classes('text-base text-secondary mb-4')

                def advance_to_next_round():
                    unsub = db.get_unsubmitted_regions(game_id, current_round)
                    if unsub:
                        with ui.dialog() as warn_dlg, ui.card():
                            ui.label('Not all regions have submitted!').classes('text-xl font-bold text-red-600 mb-2')
                            for reg in unsub:
                                ui.label(f'  • {luf_original.reg_to_long[langx][reg]}').classes('text-orange-600')
                            ui.button('OK', on_click=warn_dlg.close).props('color=primary')
                        warn_dlg.open()
                        return

                    with ui.dialog() as confirm_dlg, ui.card():
                        ui.label(luf_original.confirm_model_run[langx]).classes('text-xl font-bold mb-2')
                        ui.label(f'{luf_original.all_regions_have_submitted_run_the_model_and_advance_to_round[langx]} {current_round + 1}?')
                        ui.label('Simulation module integration pending.').classes('text-orange-600 mt-2')
                        with ui.row().classes('w-full justify-end gap-2 mt-4'):
                            ui.button('Cancel', on_click=confirm_dlg.close).props('flat color=secondary')
                            async def do_advance():
                                from nicegui import run
                                confirm_dlg.close()
                                ui.notify('Model running, please wait...', type='ongoing', timeout=0, position='center')
                                await run.io_bound(ugregmod.ugregmod, game_id, current_round)
                                db.advance_round(game_id)
                                ui.navigate.to(f'/gm/board?game_id={game_id}')
                            ui.button('Yes, Run Model', on_click=do_advance).props('color=primary')
                    confirm_dlg.open()

                ui.button(f'Advance to Round {current_round + 1}',
                         on_click=advance_to_next_round,
                         icon='arrow_forward').classes('w-full')
        card_advance.set_visibility(all_submitted_init and current_round < num_rounds)

        # ── Card 7: check_submissions_btn ─────────────────────────────────
        with ui.card().classes('w-full p-4 bg-stone-100') as card_csb:
            with ui.column():
                ui.button(luf_original.check_submissions[langx], icon='refresh',
                    on_click=lambda: refresh_board()).classes('text-lg')
        card_csb.set_visibility(not all_submitted_init)

        # ── Card 5: GM graphs ────────────────────────────────────────────
        historical_data = game_plot_ug.load_historical_data()
        plot_vars = db.get_plot_variables_for_ministry('GM')

        with ui.card().classes('w-full p-6') as card_global_graphs:
            with ui.column().classes('w-full gap-4'):
                minis = luf_original.mini_to_long[langx]
                ui.label(luf_original.historical_data[langx]).classes('text-2xl font-bold mb-1')
                ui.label(luf_original.monitoring[langx] + str(len(plot_vars)) + luf_original.indicator_for[langx] + minis.get('GM', 'Game Master')).classes('text-orange-500 font-bold mb-4')

                if plot_vars and historical_data is not None:
                    runde = 0
                    graphs_to_display = []
                    for pv in plot_vars:
                        img_data = game_plot_ug.do_graph(historical_data, pv, runde, 'glob', 'GM', langx)
                        graphs_to_display.append((pv, img_data))

                    for i in range(0, len(graphs_to_display), 2):
                        with ui.row().classes('w-full gap-4'):
                            pv, img_data = graphs_to_display[i]
                            with ui.card().classes('lg:flex-1 w-full p-4'):
                                if img_data:
                                    ui.image(img_data)
                                else:
                                    ui.label(pv['pv_indicator']).classes('text-lg font-bold')
                                    ui.label('Graph data unavailable').classes('text-sm text-orange-400 italic')

                            if i + 1 < len(graphs_to_display):
                                pv, img_data = graphs_to_display[i + 1]
                                with ui.card().classes('lg:flex-1 w-full p-4'):
                                    if img_data:
                                        ui.image(img_data)
                                    else:
                                        ui.label(pv['pv_indicator']).classes('text-lg font-bold')
                                        ui.label('Graph data unavailable').classes('text-sm text-orange-400 italic')
                            else:
                                ui.element('div').classes('lg:flex-1 w-full')

                    # GM global overlay (always full width)
                    img_data = game_plot_ug.make_glob_overlay(historical_data, lang)
                    with ui.card().classes('w-full p-4'):
                        if img_data:
                            ui.image(img_data).classes('lg:flex-1 w-full')
                        else:
                            ui.label('PROBLEM WITH Global Overlay').classes('text-lg font-bold')
        card_global_graphs.set_visibility(all_logged_init)

        # ── Card 6: Outro (game complete) ─────────────────────────────────
        with ui.card().classes('w-full p-4 bg-green-50') as card_outro:
            with ui.column():
                ui.label('This is the final round. Game complete!').classes('text-lg text-green-700 font-bold')
                ui.button('View Final Results',
                         on_click=lambda: ui.notify('Results view coming in Phase 3!'),
                         icon='assessment').classes('w-full mt-2')
        card_outro.set_visibility(game_state == 'complete')

        # ── Refresh button ────────────────────────────────────────────────
        def refresh_board():
            nl = db.get_logged(game_id, current_round)
            us = db.get_unsubmitted_regions(game_id, current_round)
            logged = len(nl) == 0
            submitted = len(us) == 0

            # Update card visibility
            card_not_logged_in.set_visibility(not logged)
            card_allow_prevent.set_visibility(logged and not submitted)
            card_advance.set_visibility(submitted and current_round < num_rounds)
            card_global_graphs.set_visibility(logged)
            card_csb.set_visibility(not submitted)
#            ui.notify(f'logged {logged}')
            if logged:
                if current_round == 1:
                    ui_gm_lab.text = luf_original.ui_gm_lab_2040[langx]
                    ui_gm_info.content = luf_original.ui_gm_info_advance[langx]
                elif current_round == 2:
                    ui_gm_lab.text = luf_original.ui_gm_lab_2060[langx]
                    ui_gm_info.content = luf_original.ui_gm_info_advance[langx]
                elif current_round == 3:
                    ui_gm_lab.text = luf_original.ui_gm_lab_2100[langx]
                    ui_gm_info.content = luf_original.ui_gm_info_advance[langx]
                else:
                    ui.notify(f'ERROR current_round is {current_round}', type='negative', close_button=True)

            # Rebuild card 2 table
            login_table_container.clear()
            if not logged:
                rows = []
                for region, minis in nl.items():
                    laf = luf_original.reg_to_long[langx][region]
                    for mini in minis:
                        rows.append({'region': laf, 'ministry': luf_original.mini_to_long[langx][mini]})
                with login_table_container:
                    ui.table(
                        columns=[
                            {'name': 'region', 'label': str(luf_original.regionluf[langx]), 'field': 'region', 'align': 'left'},
                            {'name': 'ministry', 'label': str(luf_original.ministerium[langx]), 'field': 'ministry', 'align': 'left'}
                        ],
                        rows=rows
                    ).classes('w-full text-primary').props('dense flat hide-bottom').style('background: transparent')

            # Sync card 3 switch with DB state
            if logged and not submitted:
                are_open = db.get_accept_decisions(game_id, current_round)
                accept_switch.value = are_open == 1
        # Initial populate
        refresh_board()


def show_player_ids_dialog(game_id: str, lang: str, langx: int):
    """Show dialog with list of all logged-in players"""
    regis = luf_original.regs[lang]
    with ui.dialog() as dialog, ui.card().classes('w-full max-w-2xl'):
        ui.label('Player IDs').classes('text-2xl font-bold mb-4')
        
        # Get all human players
        with db.get_db() as conn:
            cursor = conn.execute(
                """
                SELECT region_tag, ministry, username
                FROM players
                WHERE game_id = ? AND is_ai = 0
                ORDER BY region_tag, ministry
                """,
                (game_id,)
            )
            players = cursor.fetchall()
        
        if not players:
            ui.label(luf_original.no_players_have_joined_yet[langx]).classes('text-orange-600')
        else:
            # Create table
            with ui.card().classes('w-full p-4'):
                columns = [
                    {'name': 'region', 'label': 'Region', 'field': 'region', 'align': 'left'},
                    {'name': 'ministry', 'label': 'Ministry', 'field': 'ministry', 'align': 'left'},
                    {'name': 'username', 'label': 'Login ID', 'field': 'username', 'align': 'left'},
                ]
                
                rows = []
                for player in players:
                    rows.append({
                        'region': regis[player['region_tag']],
                        'ministry': player['ministry'],
                        'username': player['username']
                    })
                
                ui.table(columns=columns, rows=rows, row_key='username').classes('w-full')
        
        ui.button(luf_original.close[langx], on_click=dialog.close).classes('w-full mt-4')
    
    dialog.open()


def show_confirmation(game_id: str, lang: str, langx: int):
    """Show dialog with list of all logged-in players"""
    regis = luf_original.regs[lang]
    with ui.dialog() as dialog, ui.card().classes('w-full max-w-2xl'):
        ui.label('Info').classes('text-2xl font-bold mb-4')
        
        # Get all human players
        with db.get_db() as conn:
            cursor = conn.execute(
                """
                SELECT region_tag, ministry, username
                FROM players
                WHERE game_id = ? AND is_ai = 0
                ORDER BY region_tag, ministry
                """,
                (game_id,)
            )
            players = cursor.fetchall()
        
        if not players:
            ui.label(luf_original.no_players_have_joined_yet[langx]).classes('text-orange-600')
        else:
            # Create table
            with ui.card().classes('w-full p-4'):
                columns = [
                    {'name': 'region', 'label': 'Region', 'field': 'region', 'align': 'left'},
                    {'name': 'ministry', 'label': 'Ministry', 'field': 'ministry', 'align': 'left'},
                    {'name': 'username', 'label': 'Login ID', 'field': 'username', 'align': 'left'},
                ]
                
                rows = []
                for player in players:
                    rows.append({
                        'region': regis[player['region_tag']],
                        'ministry': player['ministry'],
                        'username': player['username']
                    })
                
                ui.table(columns=columns, rows=rows, row_key='username').classes('w-full')
        
        ui.button(luf_original.close[langx], on_click=dialog.close).classes('w-full mt-4')
    
    dialog.open()


# ============================================================================
# PLAYER - JOIN GAME
# ============================================================================
@ui.page('/player/join')
async def player_join_game():
    """Player joins a game - detect browser settings"""
    
    init_dark_mode()
    create_header()
    # Detect browser settings
    lang, langx = await detect_browser_settings()
    app.storage.tab['lang'] = lang
    app.storage.tab['langx'] = langx
    
    with ui.column().classes('w-full max-w-2xl mx-auto p-8 gap-6'):
        ui.label('Join Game').classes('text-3xl font-bold')
        
        with ui.card().classes('w-full p-6'):
            username_input = ui.input(luf_original.player_join_name[langx],
                                     placeholder=luf_original.choose_unique_username[langx]).props('autofocus').on('keydown.enter', lambda: verify_and_continue()).classes('w-full')

            game_id_input = ui.input(luf_original.gm_id_title_str[langx],
                                    placeholder=luf_original.p_enter_id_str[langx]).on('keydown.enter', lambda: verify_and_continue()).classes('w-full')
            
            error_label = ui.label('').classes('text-red-500')
            
            def verify_and_continue():
                username = username_input.value.strip()
                game_id = game_id_input.value.strip()
            
                if not username:
                    error_label.text = luf_original.please_enter_a_username[langx]
                    return
                
                if not game_id:
                    error_label.text = luf_original.please_enter_a_Game_ID[langx]
                    return
                
                # Check if username is available
                player_info = db.get_player_info(username)
                if player_info:
                    error_label.text = luf_original.username_already_taken_please_choose_another[langx]
                    return
                
                # Check if game exists and get current round
                with db.get_db() as conn:
                    cursor = conn.execute("SELECT game_id, current_round FROM games WHERE game_id = ?", (game_id,))
                    game_data = cursor.fetchone()
                    
                    if not game_data:
                        error_label.text = luf_original.no_such_game_str[langx]
                        return
                    
                    current_round = game_data[1]
                
                # Check if game has started
                if current_round == 0:
                    with ui.dialog() as dialog, ui.card():
                        ui.label(luf_original.no_such_game_str[langx])  # You'll need to add this to your language file
                        ui.button(luf_original.ok[langx], on_click=dialog.close)
                    dialog.open()
                    return
            
            # Save preferences when adding player
                db.save_player_preferences(username, 
                                      app.storage.tab['lang'], 
                                      app.storage.tab['langx'])
                # Update session
                app.storage.tab['username'] = username
                app.storage.tab['game_id'] = game_id
                app.storage.tab['role'] = 'player'
                
                # Navigate to region selection
                ui.navigate.to('/player/select_region')
            
            ui.button(luf_original.weiter[langx], on_click=verify_and_continue, 
                     icon='arrow_forward').classes('w-full')
        
        ui.button(luf_original.zurueck[langx], on_click=lambda: ui.navigate.to('/'), 
                 icon='arrow_back').classes('mt-4')


# ============================================================================
# PLAYER - RESUME GAME
# ============================================================================

@ui.page('/player/resume')
async def player_resume_game():
    """Player resumes - load saved preferences"""
    
    init_dark_mode()
    create_header()
    game_id = app.storage.tab['game_id']
    username = app.storage.tab['username']
    langx = app.storage.tab['langx']
    lang = app.storage.tab['lang']
    regis = luf_original.regs[lang]
    
    with ui.column().classes('w-full max-w-2xl mx-auto p-8 gap-6'):
        ui.label('Resume Game').classes('text-3xl font-bold')
        
        with ui.card().classes('w-full p-6'):
            username_input = ui.input('Your Username',
                                     placeholder='Enter your username').props('autofocus').on('keydown.enter', lambda: check_and_resume()).classes('w-full')
            
            error_label = ui.label('').classes('text-red-500')
            info_label = ui.label('').classes('text-orange-600')
            
            async def check_and_resume():
                username = username_input.value.strip()
                
                if not username:
                    error_label.text = 'Please enter your username'
                    return
                
                # Look up player
                player = db.get_player_info(username)
                
                if not player:
                    error_label.text = 'Username not found'
                    info_label.text = ''
                    return
                
                # Found player - show info using region_tag
                error_label.text = ''
                region_tag = player['region_tag']
                display_region = db.REGION_TAGS.get(region_tag, region_tag)
                info_label.text = f"Game: {player['game_id']} | Region: {display_region} | Ministry: {player['ministry']}"

                prefs = db.get_player_preferences(username)
                if prefs:
                    app.storage.tab['lang'] = prefs['lang']
                    app.storage.tab['langx'] = prefs['langx']
                else:
                    # Fallback to browser detection
                    lang, langx = await detect_browser_settings()
                    app.storage.tab['lang'] = lang
                    app.storage.tab['langx'] = langx
                # Update session
                app.storage.tab['username'] = username
                app.storage.tab['game_id'] = player['game_id']
                app.storage.tab['role'] = 'player'
                app.storage.tab['region_tag'] = region_tag
                app.storage.tab['ministry'] = player['ministry']
                
                # Navigate to player dashboard
                ui.navigate.to('/player/dashboard')
            
            ui.button(luf_original.resume[langx], on_click=check_and_resume, 
                     icon='login').classes('w-full mt-4')
        
        ui.button(luf_original.zurueck[langx], on_click=lambda: ui.navigate.to('/'), 
                 icon='arrow_back').classes('mt-4')


# ============================================================================
# PLAYER - SELECT REGION
# ============================================================================

@ui.page('/player/select_region')
def player_select_region():
    """Player selects region and ministry"""
    
    init_dark_mode()
    create_header()
    if not app.storage.tab.get('game_id') or app.storage.tab.get('role') != 'player':
        ui.navigate.to('/')
        return
    
    game_id = app.storage.tab['game_id']
    username = app.storage.tab['username']
    langx = app.storage.tab['langx']
    lang = app.storage.tab['lang']
    regis = luf_original.regs[lang]
    minis = luf_original.minis[lang]
    
    with ui.column().classes('w-full max-w-4xl mx-auto p-8 gap-6'):
        willkommen = luf_original.welcome[langx]
        spiel = luf_original.game[langx]
        ui.label(f'{willkommen}, {username}!').classes('text-3xl font-bold')
        ui.label(f'{spiel}: {game_id}').classes('text-xl text-orange-600 font-mono')
        
        ui.separator()
        
        ui.label(luf_original.select_your_region_and_ministry[langx]).classes('text-xl font-bold mb-4')
#        ui.label(luf.choose_an_available_position_to_begin_playing[langx]).classes('text-orange-600 mb-4')
        
        available = db.get_available_regions_ministries(game_id)
        
        if not available:
            ui.label(luf_original.no_positions_available_game_is_full[langx]).classes('text-red-600 font-bold')
            ui.button(luf_original.zurueck[langx], on_click=lambda: ui.navigate.to('/'), 
                     icon='arrow_back').classes('mt-4')
            return
        
        error_label = ui.label('').classes('text-red-500')
        
        # Create selection UI using region_tag
        with ui.column().classes('w-full gap-4'):
            for region_tag, ministries in sorted(available.items()):
                display_name = regis[region_tag]
                
                with ui.card().classes('w-full p-4'):
                    ui.label(display_name).classes('text-xl font-bold mb-2')
                    
                    with ui.row().classes('w-full gap-2 flex-wrap'):
                        for ministry in ministries:
                            def make_select_handler(r_tag, m):
                                def handler():
                                    # Try to add player using region_tag
                                    success = db.add_player(game_id, username, r_tag, m, 1, is_ai=False)
                                    
                                    if success:
                                        app.storage.tab['region_tag'] = r_tag
                                        app.storage.tab['ministry'] = m
                                        if m == 'Future':
                                            ui.navigate.to('/future/dashboard')
                                        else:
                                            ui.navigate.to('/player/dashboard')
                                    else:
                                        error_label.text = luf_original.error_label_tx[langx]
                                
                                return handler
                            
                            ui.button(minis[ministry], 
                                     on_click=make_select_handler(region_tag, ministry),
                                     icon='check_circle').classes('flex-grow')
        
        ui.button(luf_original.zurueck[langx], on_click=lambda: ui.navigate.to('/'), 
                 icon='arrow_back').classes('mt-4')


# ============================================================================
# PLAYER - DASHBOARD
# ============================================================================

@ui.page('/player/dashboard')
def player_dashboard():
    """Player dashboard - policy management and plot variables"""
    
    init_dark_mode()
    create_header()
    if not app.storage.tab.get('game_id') or app.storage.tab.get('role') != 'player':
        ui.navigate.to('/')
        return
    
    username = app.storage.tab['username']
    game_id = app.storage.tab['game_id']
    region_tag = app.storage.tab['region_tag']
    ministry = app.storage.tab['ministry']
    langx = app.storage.tab['langx']
    lang = app.storage.tab['lang']
    regis = luf_original.regs[lang]
    minis = luf_original.minis[lang]
    pol_expls = luf_original.pols_expl[lang]
    pol_names = luf_original.pols_name[lang]
    display_region = regis[region_tag]

    # Get game info
    game_info = db.get_game_info(game_id)
    current_round = game_info['current_round']

    # Mark this player as logged in for this round
    db.mark_player_submission(game_id, username, current_round)

    # If round is 0, we're in setup - go to round 1
    if current_round == 0:
        current_round = 1
    
    # Load historical data (1990-2025)
    historical_data = game_plot_ug.load_historical_data()
    
    with ui.column().classes('w-full max-w-6xl mx-auto p-8 gap-6'):
        # Header
        with ui.row().classes('w-full items-center justify-between'):
            with ui.column().classes('gap-1'):
                ui.label(f'{username}').classes('text-3xl font-bold')
                ui.label(f'{display_region} - {ministry}').classes('text-2xl text-orange-600')
                ui.label(luf_original.game[langx] + ': ' + game_id + ' | ' + luf_original.runde[langx] + ': '+str(current_round)).classes('text-lg text-orange-400 font-mono')
#                ui.label(f'Game: {game_id} | Round: {current_round}').classes('text-lg text-gray-600 font-mono')
        
        ui.separator()
        
        # Status message
        status_label = ui.label('').classes('text-lg font-bold')

        # ===================================================================
        # MODEL RESULTS SECTION - auto-appears when model has run
        # ===================================================================
        plot_vars = db.get_plot_variables_for_ministry(ministry)

        @ui.refreshable
        def render_results():
            res_data, res_runde = game_plot_ug.load_game_data(game_id, current_round - 1)
            if res_runde >= 1:
                with ui.expansion(
                    f'Check the results for Round {res_runde}',
                    icon='bar_chart'
                ).classes('w-full text-xl font-bold'):
                    with ui.card().classes('w-full p-6'):
                        with ui.column().classes('w-full gap-4'):
                            res_graphs = []
                            for pv in plot_vars:
                                img = game_plot_ug.do_graph(res_data, pv, res_runde, region_tag, ministry, langx)
                                res_graphs.append((pv, img))
                            for i in range(0, len(res_graphs), 2):
                                with ui.row().classes('w-full gap-4'):
                                    pv, img = res_graphs[i]
                                    with ui.card().classes('lg:flex-1 w-full p-4'):
                                        if img:
                                            ui.image(img)
                                        else:
                                            ui.label(pv['pv_indicator']).classes('text-lg font-bold')
                                            ui.label('Graph data unavailable').classes('text-sm text-orange-400 italic')
                                    if i + 1 < len(res_graphs):
                                        pv, img = res_graphs[i + 1]
                                        with ui.card().classes('lg:flex-1 w-full p-4'):
                                            if img:
                                                ui.image(img)
                                            else:
                                                ui.label(pv['pv_indicator']).classes('text-lg font-bold')
                                                ui.label('Graph data unavailable').classes('text-sm text-orange-400 italic')
                                    else:
                                        ui.element('div').classes('lg:flex-1 w-full')
            return res_runde if 'res_runde' in dir() else 0

        render_results()

        # ===================================================================
        # HISTORICAL GRAPHS SECTION - hidden once results are available
        # ===================================================================
        _, init_runde = game_plot_ug.load_game_data(game_id, current_round - 1)

        with ui.column() as hist_container:
            if plot_vars and historical_data is not None:
                runde = 0
                with ui.card().classes('w-full p-6'):
                    ui.label(luf_original.historical_data[langx]).classes('text-2xl font-bold mb-1')
                    ui.label(luf_original.monitoring[langx]+ str(len(plot_vars)) + luf_original.indicator_for[langx] + minis[ministry]).classes('text-orange-500 font-bold mb-4')
                    ui.markdown(luf_original.pcgd_rd1_info_tx_str[langx])
                    with ui.column().classes('w-full gap-4'):
                        graphs_to_display = []
                        for pv in plot_vars:
                            img_data = game_plot_ug.do_graph(historical_data, pv, runde, region_tag, ministry, langx)
                            graphs_to_display.append((pv, img_data))
                        for i in range(0, len(graphs_to_display), 2):
                            with ui.row().classes('w-full gap-4'):
                                pv, img_data = graphs_to_display[i]
                                with ui.card().classes('lg:flex-1 w-full p-4'):
                                    if img_data:
                                        ui.image(img_data)
                                    else:
                                        ui.label(pv['pv_indicator']).classes('text-lg font-bold')
                                        ui.label('Graph data unavailable').classes('text-sm text-orange-400 italic')
                                if i + 1 < len(graphs_to_display):
                                    pv, img_data = graphs_to_display[i + 1]
                                    with ui.card().classes('lg:flex-1 w-full p-4'):
                                        if img_data:
                                            ui.image(img_data)
                                        else:
                                            ui.label(pv['pv_indicator']).classes('text-lg font-bold')
                                            ui.label('Graph data unavailable').classes('text-sm text-orange-400 italic')
                                else:
                                    ui.element('div').classes('lg:flex-1 w-full')
                        if ministry == 'GM':
                            img_data = game_plot_ug.make_glob_overlay(historical_data, 'no')
                            with ui.card().classes('w-full p-4'):
                                if img_data:
                                    ui.image(img_data).classes('lg:flex-1 w-full')
                                else:
                                    ui.label('PROBLEM WITH Global OVERlay').classes('text-lg font-bold')

        hist_container.set_visibility(init_runde < 1)

        # Poll every 5 s — show results expansion and hide historical when model finishes
        _prev_runde = [init_runde]
        def _check_results():
            _, runde = game_plot_ug.load_game_data(game_id, current_round - 1)
            if runde > _prev_runde[0]:
                _prev_runde[0] = runde
                render_results.refresh()
                hist_container.set_visibility(False)
                _results_timer.cancel()
        _results_timer = ui.timer(5.0, _check_results)

        ui.separator()

        # ===================================================================
        # POLICY SLIDERS SECTION - With integrated target/threshold
        # ===================================================================

        @ui.refreshable
        def slider_section():
            if db.is_region_submitted(game_id, current_round, region_tag):
                with ui.card().classes('w-full p-4'):
                    ui.label('All investment proposals for your region have been submitted.').classes('text-xl font-bold text-green-700 dark:text-green-300')
                return

            if current_round == 1:
                rrange = luf_original.now_2040[langx]
            elif current_round == 2:
                rrange = luf_original.to_2060[langx]
            elif current_round == 3:
                rrange = luf_original.to_2100[langx]

            slider_metadata = {}

            def handle_slider_change(e):
                try:
                    metadata = slider_metadata.get(e.sender.id)
                    if metadata:
                        db.save_policy_decision_from_slider(
                            metadata['game_id'],
                            metadata['current_round'],
                            metadata['region_tag'],
                            metadata['ministry'],
                            metadata['pol_id'],
                            e.value,
                            metadata['pol_tag']
                        )
                    else:
                        ui.notify(f"No metadata found for slider {e.sender.id}", type='warning')
                except Exception as ex:
                    ui.notify(f"Error: {str(ex)}", type='negative')
                    print(f"Slider error: {ex}")

            policies = db.get_policies_for_ministry(ministry)

            with ui.card().classes('w-full p-2'):
                ui.label(f'{luf_original.pol_decs[langx]} - {display_region} - {ministry}').classes('text-2xl font-bold mb-2')
                ui.label(luf_original.dec_title_tx_str[langx]+str(current_round)+rrange).classes('text-lg text-orange-700 mb-4')
                ui.markdown(luf_original.dec_info_tx_str[langx])

                if not policies:
                    ui.label(f'No policies assigned to {ministry}').classes('text-red-600')
                else:
                    for policy in policies:
                        pol_id  = policy['pol_id']
                        pol_tag = policy['pol_tag']
                        pol_min = policy['pol_min']
                        pol_max = policy['pol_max']

                        current_value = db.get_one_policy_decision(game_id, current_round, region_tag, ministry, pol_tag)

                        with ui.card().classes('w-full mb-1 bg-gray-50 text-base text-orange-600 font-bold').tight():
                            expansion = ui.expansion(policy['pol_name'], icon='info').classes('w-full font-bold')
                            expansion.props('header-class="dark:text-primary text-primary"')
                            with expansion:
                                ui.label(pol_expls[pol_tag]).classes('text-base text-orange-600 font-bold')

                            with ui.row().classes('w-full items-center gap-4'):
                                ui.label(f'{pol_min}').classes('text-base text-orange-700 w-12 text-right')

                                with ui.element('div').classes('flex-grow relative'):
                                    slider = ui.slider(
                                        min=pol_min,
                                        max=pol_max,
                                        value=current_value,
                                        step=(pol_max - pol_min) / 10,
                                        on_change=handle_slider_change
                                    ).props('label-always').classes('w-full relative z-10')

                                    slider_metadata[slider.id] = {
                                        'game_id':       game_id,
                                        'current_round': current_round,
                                        'pol_id':        pol_id,
                                        'pol_tag':       pol_tag,
                                        'region_tag':    region_tag,
                                        'ministry':      ministry
                                    }

                                ui.label().bind_text_from(slider, 'value').classes('text-lg font-mono text-green-600 w-20')
                                ui.label(f'{pol_max}').classes('text-base text-orange-600 w-12')

        slider_section()

        def _poll_submission():
            if db.is_region_submitted(game_id, current_round, region_tag):
                slider_section.refresh()
                poll_timer.cancel()

        poll_timer = ui.timer(5.0, _poll_submission)


# ============================================================================
# FUTURE - DASHBOARD
# ============================================================================

@ui.page('/future/dashboard')
def future_dashboard():
    """Future dashboard - controls submissions from other reg_players to be in budget and plot variables"""
    
    init_dark_mode()
    create_header()
    if not app.storage.tab.get('game_id') or app.storage.tab.get('role') != 'player':
        ui.navigate.to('/')
        return
    
    grand_total = 0.0
    username = app.storage.tab['username']
    game_id = app.storage.tab['game_id']
    region_tag = app.storage.tab['region_tag']
    ministry = app.storage.tab['ministry']
    langx = app.storage.tab['langx']
    lang = app.storage.tab['lang']
    regis = luf_original.regs[lang]
    minis = luf_original.minis[lang]
    pol_expls = luf_original.pols_expl[lang]
    pol_names = luf_original.pols_name[lang]
    display_region = regis[region_tag]

    # Get game info
    game_info = db.get_game_info(game_id)
    current_round = game_info['current_round']

    # Mark this player as logged in for this round
    db.mark_player_submission(game_id, username, current_round)

    # If round is 0, we're in setup - go to round 1
    if current_round == 0:
        current_round = 1
    
    # Load historical data (1990-2025)
    historical_data = game_plot_ug.load_historical_data()
    
    with ui.column().classes('w-full max-w-6xl mx-auto p-2 gap-2'):
        # Header
        with ui.row().classes('w-full items-center justify-between'):
            with ui.column().classes('gap-1'):
                ui.label(f'{username}').classes('text-3xl font-bold')
                ui.label(f'{display_region} - {ministry}').classes('text-2xl text-orange-600')
                ui.label(luf_original.game[langx] + ': ' + game_id + ' | ' + luf_original.runde[langx] + ': '+str(current_round)).classes('text-lg text-orange-400 font-mono')
        
        ui.separator()
        
        # Status message
        status_label = ui.label('').classes('text-lg font-bold')
        
        # ===================================================================
        # HISTORICAL GRAPHS SECTION - Show before sliders
        # ===================================================================
        
        # Get plot variables for this ministry
        plot_vars = db.get_plot_variables_for_ministry(ministry)
        
        if plot_vars and historical_data is not None:
            runde = 0
            with ui.card().classes('w-full p-6'):
                ui.label(luf_original.historical_data[langx]).classes('text-2xl font-bold mb-4')
                ui.label(luf_original.monitoring[langx]+ str(len(plot_vars)) + luf_original.indicator_for[langx] + minis[ministry]).classes('text-orange-500 font-bold mb-4')
                ui.markdown(luf_original.fut_top_info[langx])
#                ui.markdown(luf.pcgd_rd1_info_fut_tx_str[langx])
                
                # Display graphs
                with ui.column().classes('w-full gap-4'):
                    # Group graphs in pairs for larger screens
                    graphs_to_display = []
                    for pv in plot_vars:
                        img_data = game_plot_ug.do_graph(historical_data, pv, runde, region_tag, ministry, langx)
                        graphs_to_display.append((pv, img_data))
                        
                    
                    # Display graphs in rows of 2 on larger screens
                    for i in range(0, len(graphs_to_display), 2):
                        with ui.row().classes('w-full gap-4'):
                            # First graph
                            pv, img_data = graphs_to_display[i]
                            with ui.card().classes('lg:flex-1 w-full p-4'):
                                if img_data:
                                    ui.image(img_data)
                                else:
                                    ui.label(pv['pv_indicator']).classes('text-lg font-bold')
                                    ui.label('Graph data unavailable').classes('text-sm text-orange-400 italic')
                            
                            # Second graph (if exists)
                            if i + 1 < len(graphs_to_display):
                                pv, img_data = graphs_to_display[i + 1]
                                with ui.card().classes('lg:flex-1 w-full p-4'):
                                    if img_data:
                                        ui.image(img_data)
                                    else:
                                        ui.label(pv['pv_indicator']).classes('text-lg font-bold')
                                        ui.label('Graph data unavailable').classes('text-sm text-orange-400 italic')
                            else:
                                # Add invisible spacer to keep sizing consistent
                                ui.element('div').classes('lg:flex-1 w-full')
                                
                    # GM global overlay (always full width)
                    if ministry == 'GM':
                        img_data = game_plot_ug.make_glob_overlay(historical_data, 'no')
                        with ui.card().classes('w-full p-4'):
                            if img_data:
                                ui.image(img_data).classes('lg:flex-1 w-full')
                            else:
                                ui.label('PROBLEM WITH Global OVERlay').classes('text-lg font-bold')
        ui.separator()
        
        # ===================================================================
        # STATUS BUTTON - below graphs, refreshable
        # Single button that shows either: missing players OR investment plans
        # ===================================================================

        grand_total = [0.0]

        def show_investment_plans_dialog():
            """Open a dialog showing all ministries' investment plans for this region"""
            budget_data = db.get_budget_by_ministry_and_policy(game_id, current_round, region_tag)

            with ui.dialog() as inv_dialog, ui.card().classes('w-full max-w-3xl'):
                ui.label(luf_original.budget_considerations[langx] + ' – ' + luf_original.reg_to_long[langx][region_tag]).classes('text-2xl font-bold mb-4')

                if not budget_data:
                    ui.label('No investment data yet.').classes('text-orange-400 italic')
                else:
                    running_total = 0.0
                    for ministry_name, ministry_info in budget_data.items():
                        ministry_total = ministry_info['total']
                        running_total += ministry_total
                        with ui.expansion(f'{ministry_name}  –  {luf_original.total[langx]} {ministry_total:.1f}',
                                          icon='account_balance').classes('w-full'):
                            with ui.card().classes('w-full'):
                                policy_rows = [
                                    {
                                        'policy': policy['name'],
                                        'value':  f'{policy["value"]:.1f}',
                                        'amount': f'{policy["amount"]:.1f}'
                                    }
                                    for policy in ministry_info['policies']
                                ]
                                policy_columns = [
                                    {'name': 'policy', 'label': luf_original.policy[langx],    'field': 'policy', 'align': 'left'},
                                    {'name': 'value',  'label': luf_original.pct_value[langx], 'field': 'value',  'align': 'right'},
                                    {'name': 'amount', 'label': luf_original.amount2[langx],   'field': 'amount', 'align': 'right'},
                                ]
                                ui.table(columns=policy_columns, rows=policy_rows, row_key='policy').classes('w-full')

                    # Grand total row at the bottom
                    ui.separator()
                    ui.label(f'{luf_original.your_budget[langx]}  –  {luf_original.total[langx]}: {running_total:.1f}').classes('text-xl font-bold mt-2')

                ui.button(luf_original.close[langx], on_click=inv_dialog.close).classes('w-full mt-4')

            inv_dialog.open()

        @ui.refreshable
        def status_button_section():
            still_missing = db.get_logged_for_reg(game_id, current_round, region_tag)

            with ui.row().classes('w-full justify-center my-4 gap-4'):
                if len(still_missing) > 0:
                    # Some players haven't logged in yet
                    minis = luf_original.mini_to_long[langx]
                    missing_names = ', '.join(minis[m] for m in still_missing)
                    ui.label(f'⚠  {luf_original.Ooops[langx]}: {missing_names}').classes('text-primary font-bold self-center')
                    ui.button(
                        f'{luf_original.check_your_teams_log_ins[langx]}  ({len(still_missing)})',
                        icon='warning',
                        on_click=lambda: (
                            show_still_missing(lang, langx, game_id, current_round, region_tag),
                            status_button_section.refresh(),
                            budget_section.refresh()
                        )
                    ).props('color=secondary')
                else:
                    ui.label('All team members are logged in.').classes('text-green-700 font-bold')

        status_button_section()

        ui.separator()

        # ===================================================================
        # BUDGET SECTION - full submission workflow
        # ===================================================================

        @ui.refreshable
        def budget_section():
            still_missing = db.get_logged_for_reg(game_id, current_round, region_tag)
#            ui.notify(still_missing)

            if len(still_missing) > 0:
                pass
#                ui.notify('formerly wrong flow', type='info')
#                with ui.card().classes('lg:flex-1 w-full p-2'):
#                    ui.label(luf.Ooops[langx]).classes('text-lg font-bold')
#                    ui.markdown(luf.some_of_your_team[langx])
#                    ui.button(
#                        luf.check_your_teams_log_ins[langx],
#                        icon='cached',
#                        on_click=lambda: (
#                            show_still_missing(lang, langx, game_id, current_round, region_tag),
#                            budget_section.refresh(),
#                            status_button_section.refresh()   # keep the top button in sync too
#                        )
#                    ).props('color=secondary')
            else:
                # Get budget for this round
                if current_round == 1:
                    rrange = luf_original.now_2040[langx]
                    budg = db.get_budget('START', 0, region_tag, 'bud')
                elif current_round == 2:
                    rrange = luf_original.to_2060[langx]
                    budg = db.get_budget(game_id, 1, region_tag, 'bud')
                elif current_round == 3:
                    rrange = luf_original.to_2100[langx]
                    budg = db.get_budget(game_id, 2, region_tag, 'bud')
                bud = float(budg[0])
#                bud = 10.0  # ← your test override

                # ── Already submitted: show locked card ──────────────────
                if db.is_region_submitted(game_id, current_round, region_tag):
                    with ui.card().classes('w-full p-4 gap-3'):
                        ui.label('All investment proposals for your region have been submitted.').classes('text-xl font-bold text-green-700 dark:text-green-300 mb-2')

                        model_status = ui.column().classes('w-full')

                        def check_model_advanced():
                            model_status.clear()
                            live_round = db.get_game_info(game_id)['current_round']
                            with model_status:
                                if live_round > current_round:
                                    ui.label('The model has been advanced. Dashboard refresh coming soon (model_run.py integration pending).').classes('text-green-600 font-bold')
                                else:
                                    ui.label('Please wait until the model has been advanced.').classes('text-orange-600 font-bold')

                        ui.button(
                            'Check if the model has been advanced by the GM',
                            icon='query_stats',
                            on_click=check_model_advanced
                        ).props('color=primary')

                # ── Not yet submitted: show proposals workflow ────────────
                else:
                    with ui.card().classes('w-full p-4 gap-3'):
                        laf = luf_original.reg_to_long[langx][region_tag]
                        ui.label(luf_original.budget_considerations[langx] + ', ' + laf).classes('text-2xl font-bold')
                        ui.label(luf_original.bud_title_tx_str[langx] + str(current_round) + rrange).classes('text-blue-600 dark:text-orange-500 text-lg')

                        # ── "Check" button first ──────────────────────────────────
                        ui.button(luf_original.check_your_colleagues_investment_proposals[langx],
                            icon='refresh',
                            on_click=lambda: load_proposals()
                        ).props('color=primary')

                        # ── Two containers: proposals then summary ────────────────
                        proposals_container = ui.column().classes('w-full gap-2')
                        summary_container   = ui.column().classes('w-full')

                        # ── Helpers ───────────────────────────────────────────────
                        def submit_proposals():
                            is_allowed = db.get_accept_decisions(game_id, current_round, region_tag)
                            if is_allowed == 0:
                                # not allowed
                                ui.notify(luf_original.ooops_GM_changed_mind[langx], type='negative', close_button=True, position='center')
                                return
                            with ui.dialog() as confirm_dialog, ui.card():
                                ui.label(luf_original.confirm_submission[langx]).classes('text-xl font-bold mb-2')
                                ui.label(luf_original.are_you_sure_you_want_to_submit_all_investment_proposals[langx])
                                ui.label(f'{luf_original.budget2[langx]}: {bud:.1f}')
                                ui.label(f'{luf_original.total2[langx]}: {grand_total[0]:.1f}')
                                ui.label(luf_original.once_submitted[langx]).classes('text-orange-600 mt-2')
                                with ui.row().classes('w-full justify-end gap-2 mt-4'):
                                    ui.button(luf_original.cancel_btn[langx], on_click=confirm_dialog.close).props('flat color=secondary')
                                    ui.button(luf_original.yes_submit[langx],
                                             on_click=lambda: confirm_and_submit(confirm_dialog)).props('color=primary')
                            confirm_dialog.open()

                        async def confirm_and_submit(dialog):
                            try:
                                db.mark_region_submitted(game_id, current_round, region_tag)
                                dialog.close()
                                budget_section.refresh()
                            except Exception as e:
                                dialog.close()
                                with ui.dialog() as error_dialog, ui.card():
                                    ui.label('Submission Error').classes('text-xl font-bold text-red-600 mb-2')
                                    ui.label(f'An error occurred: {str(e)}')
                                    ui.button('OK', on_click=error_dialog.close).props('color=primary')
                                error_dialog.open()

                        def load_proposals():
                            proposals_container.clear()
                            summary_container.clear()
                            grand_total[0] = 0.0

                            _, _, _, raw_results = get_tab(game_id, current_round, region_tag)

                            with proposals_container:
                                for ministry_name, policies in raw_results.items():
                                    ministry_total = sum(policies.values())
                                    grand_total[0] += ministry_total

                                    with ui.expansion(
                                        f'{ministry_name}  –  {luf_original.total[langx]}: {ministry_total:.1f}',
                                        icon='account_balance'
                                    ).classes('w-full'):
                                        with ui.card().classes('w-full'):
                                            policy_rows = [
                                                {
                                                    'policy': tag,
                                                    'value':  f'{get_inv_props(game_id, current_round, region_tag, ministry_name, tag) * 100:.1f}',
                                                    'amount': f'{amount:.1f}'
                                                }
                                                for tag, amount in policies.items()
                                            ]
                                            policy_columns = [
                                                {'name': 'policy', 'label': luf_original.policy[langx],    'field': 'policy', 'align': 'left'},
                                                {'name': 'value',  'label': luf_original.pct_value[langx], 'field': 'value',  'align': 'right'},
                                                {'name': 'amount', 'label': luf_original.amount2[langx],   'field': 'amount', 'align': 'right'},
                                            ]
                                            ui.table(columns=policy_columns, rows=policy_rows, row_key='policy').classes('w-full')

                            with summary_container:
                                # Check if GM has allowed submissions
                                submissions_allowed = db.get_accept_decisions(game_id, current_round, region_tag)

                                if submissions_allowed != 1:
                                    with ui.card().classes('w-full bg-yellow-50 dark:bg-yellow-900 p-3'):
                                        ui.label(luf_original.submit_proposals[langx]).classes('text-orange-700 dark:text-orange-300 text-lg font-bold')
                                elif grand_total[0] <= bud:
                                    with ui.card().classes('w-full bg-green-50 dark:bg-green-900 p-3'):
                                        ui.label(
                                            f'{luf_original.your_budget[langx]} {bud:.1f}  –  '
                                            f'{luf_original.all_investment_plans_summed_up_for_your_region[langx]} {grand_total[0]:.1f}'
                                        ).classes('text-xl font-bold text-green-700 dark:text-green-300 mb-2')
                                        ui.button(luf_original.submit_plans2[langx], icon='send',
                                                  on_click=submit_proposals).props('color=green')
                                else:
                                    with ui.card().classes('w-full bg-orange-50 dark:bg-orange-900 p-3'):
                                        plans = luf_original.plans[langx]
                                        plans2 = luf_original.plans2[langx]
                                        plans3 = luf_original.plans3[langx]
                                        lab = f"{plans}{grand_total[0]:.1f}{plans2}{bud:.1f}{plans3}"
                                        ui.label(lab).classes('text-orange-700 dark:text-orange-300 text-lg font-bold')

                        load_proposals()  # populate on first render

        budget_section()  # render it
# ============================================================================
# About
# ============================================================================

@ui.page('/about')
def about_page():
    init_dark_mode()
    create_header()
     
    with ui.column().classes('w-full max-w-4xl mx-auto p-8 gap-6 items-center'):
        # Centered markdown content
        ui.markdown(luf_original.about_md[app.storage.tab['langx']]).classes('w-full')
        # Back button
        ui.button(luf_original.btn_back[app.storage.tab['langx']], 
                 on_click=lambda: ui.navigate.back(),
                 icon='arrow_back').classes('mt-4')
        
# ============================================================================
# Legal
# ============================================================================

@ui.page('/legal')
async def legal_page():
    await ui.context.client.connected()
    init_dark_mode()
    create_header()
     
    with ui.column().classes('w-full max-w-4xl mx-auto p-8 gap-6 items-center'):
        # Centered markdown content
        ui.markdown(luf_original.legal_md[app.storage.tab['langx']]).classes('w-full')
        # Back button
        ui.button(luf_original.btn_back[app.storage.tab['langx']], 
                 on_click=lambda: ui.navigate.back(),
                 icon='arrow_back').classes('mt-4')
        
# ============================================================================
# DEV - DATABASE INSPECTOR
# ============================================================================

@ui.page('/dev/db')
def dev_db_page():
    """Live database inspector – auto-refreshes every 3 s."""
    init_dark_mode()

    def make_table(conn, label, sql, abbrev=None):
        """Render a labelled db table. abbrev maps col name → short header."""
        ui.label(label).classes('text-base font-bold font-mono text-orange-500 mt-4 mb-1')
        rows = [dict(r) for r in conn.execute(sql).fetchall()]
        if not rows:
            ui.label('(empty)').classes('text-gray-400 italic text-sm')
            return
        keys = list(rows[0].keys())
        cols = [{'name': k, 'label': (abbrev or {}).get(k, k), 'field': k, 'align': 'left'} for k in keys]
        ui.table(columns=cols, rows=rows).classes('w-full font-mono').props('dense flat separator="cell" hide-bottom')

    with ui.column().classes('w-full max-w-7xl mx-auto p-4 gap-2'):
        with ui.row().classes('w-full items-center gap-4'):
            ui.label('DB Inspector').classes('text-2xl font-bold font-mono')
            ui.label('auto-refresh 3 s').classes('text-sm text-gray-400')
            ui.button('Refresh now', icon='refresh', on_click=lambda: tables.refresh()).props('flat dense')

        @ui.refreshable
        def tables():
            with db.get_db() as conn:
                make_table(conn, 'games',
                    'SELECT game_id, current_round, num_rounds, state, accept_decisions, state_x, created_at FROM games ORDER BY created_at DESC')

                make_table(conn, 'human_regions  (sub_N = submissions allowed)',
                    'SELECT game_id, region_tag, sub_1, sub_2, sub_3 FROM human_regions ORDER BY game_id, region_tag')

                make_table(conn, 'players  (human, login flags)',
                    'SELECT game_id, region_tag, ministry, username, is_logged_in_round1 AS log1, is_logged_in_round2 AS log2, is_logged_in_round3 AS log3, state_x FROM players WHERE is_ai=0 ORDER BY game_id, region_tag, ministry',
                    abbrev={'is_logged_in_round1': 'log1', 'is_logged_in_round2': 'log2', 'is_logged_in_round3': 'log3'})

                make_table(conn, 'region_submissions',
                    'SELECT game_id, round_num, region_tag, submitted_at FROM region_submissions ORDER BY game_id, round_num, region_tag')

#                make_table(conn, 'policy_decisions  (row count per game/round)',
#                    'SELECT game_id, round, region_tag, ministry, COUNT(*) AS n_decisions FROM policy_decisions GROUP BY game_id, round, region_tag, ministry ORDER BY game_id, round, region_tag, ministry')

        tables()
        ui.timer(3.0, tables.refresh)

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ in {"__main__", "__mp_main__"}:
    # Initialize database
#    db.init_database()
#    db.load_policies_data()
#    db.load_plot_variables_data()
    
    # Run NiceGUI app
    ui.run(
        title='SimFuture',
        favicon='🌍',
        dark=None,  # Auto-detect dark mode
        reload=False,
        show=True,
        storage_secret='freitag',
        port=8888  # Use port 8888 to avoid Windows permission issues
    )
