import streamlit as st
import time

def is_valid_email(email):
    """Validate email is real-looking, not fake."""
    import re
    if not email or "@" not in email:
        return False, "Please enter a valid email address."
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format."
    local, domain = email.split("@", 1)
    if len(local) < 2:
        return False, "Email username too short."
    fake_domains = ["test.com", "fake.com", "example.com", "abc.com", "xyz.com", "temp.com", "asdf.com", "none.com"]
    if domain.lower() in fake_domains:
        return False, f"Please use a real email, not @{domain}"
    if domain.count(".") < 1 or len(domain.split(".")[-1]) < 2:
        return False, "Invalid email domain."
    return True, ""

def page_login():
    from ui_components import render_back_button
    
    col1,col2,col3 = st.columns([1,2,1])
    with col2:
        greeting = "Welcome Back 👋" if st.session_state.logged_in else "Welcome 👋"
        st.markdown(f"""<div style="background:var(--bg-card);border:1px solid var(--border);border-radius:16px;padding:36px;margin-top:40px">
          <div class="login-greeting">{greeting}</div>
          <div class="login-sub">Sign in to unlock all features including AI analysis & watchlist</div>
        </div>""", unsafe_allow_html=True)

        email = st.text_input("Email address", placeholder="yourname@gmail.com", key="login_email")
        name = st.text_input("Your name", placeholder="Rahul Sharma", key="login_name")

        if st.button("🚀 Login", key="email_login", use_container_width=True):
            valid, err_msg = is_valid_email(email)
            if valid:
                if not name or len(name.strip()) < 2:
                    st.error("Please enter your name (at least 2 characters).")
                else:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email.strip()
                    st.session_state.user_name = name.strip()
                    if "cookie_controller" in st.session_state and st.session_state.cookie_controller is not None:
                        st.session_state.cookie_controller.set("ss_email", email.strip())
                        st.session_state.cookie_controller.set("ss_name", name.strip())
                    st.success(f"Welcome aboard, {st.session_state.user_name}! 🎉")
                    time.sleep(0.6)
                    st.session_state.page = st.session_state.prev_page or "home"
                    st.rerun()
            else:
                st.error(err_msg)

        st.markdown('<div class="divider"><hr/><span>or</span><hr/></div>', unsafe_allow_html=True)

        st.markdown("""<div style="background:rgba(232,168,56,.06);border:1px solid rgba(232,168,56,.15);border-radius:10px;padding:12px 16px;margin-bottom:12px">
          <span style="color:#E8A838;font-weight:600;font-size:13px">👤 Guest Mode</span><br>
          <span style="color:#9E9E9E;font-size:12px">Browse stocks, screeners & charts — but <strong>AI Analysis</strong> and <strong>Watchlist</strong> require login.</span>
        </div>""", unsafe_allow_html=True)

        if st.button("👤 Continue as Guest", key="skip_login", use_container_width=True, type="secondary"):
            st.session_state.logged_in = False
            st.session_state.user_name = "Guest"
            st.session_state.page = st.session_state.prev_page or "home"
            st.rerun()

        render_back_button("← Back")

        st.markdown('<div style="color:#616161;font-size:11px;text-align:center;margin-top:16px">🔒 Your data is stored securely. We never share your information.</div>', unsafe_allow_html=True)
