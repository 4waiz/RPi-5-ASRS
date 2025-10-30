<script>
    let { AlertsNum, WoriginNum,  } = $props();

    const clearSelection = () => {
        if (typeof window === "undefined") return;
        const selection = window.getSelection?.();
        selection?.removeAllRanges?.();
    };

    const releaseFocus = (element) => {
        element?.blur?.();
        clearSelection();
    };

    const handleKeydown = (event) => {
        const blockedKeys = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "Home", "End"];
        if (blockedKeys.includes(event.key)) {
            event.preventDefault();
            releaseFocus(event.currentTarget);
        }
    };
</script>

<nav class="sidebar">
    <div class="logo-section">
        <img src="\src\assets\Edge_logo.png" alt="Egde Logo" height="70px" />
    </div>

    <div class="nav-menu">
        <div class="nav-item active">
            <svg class="nav-icon" viewBox="0 0 24 24">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
            Home
        </div>

        <div class="nav-item">
            <svg class="nav-icon" viewBox="0 0 24 24">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
            </svg>
            Alerts
            <div class="badge-container">
                <span class="badge red">{AlertsNum}</span>
                <span class="badge yellow">{WoriginNum}</span>
            </div>
        </div>

        <div class="nav-item">
            <svg class="nav-icon" viewBox="0 0 24 24">
                <path
                    d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
                ></path>
                <circle cx="9" cy="10" r="1"></circle>
                <circle cx="12" cy="10" r="1"></circle>
                <circle cx="15" cy="10" r="1"></circle>
            </svg>
            AI Assistant
        </div>
    </div>

    <button
        class="settings-btn"
        onclick={(event) => releaseFocus(event.currentTarget)}
        onfocus={(event) => releaseFocus(event.currentTarget)}
        onkeydown={handleKeydown}
    >
        <svg
            class="settings-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
        >
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M12 1v6m0 6v6m-8-8h6m6 0h6"></path>
            <path
                d="M12 1l3.09 3.09M18.91 5.91L21 8m0 8l-2.09 2.09M15.91 20.91L12 23m-3.09-3.09L5.91 18.91M3 16l-2-2M3 8L1 6m4.91-3.09L9.09 1"
            ></path>
        </svg>
        Settings
    </button>
</nav>

<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

.sidebar {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: flex-start;
    width: fit-content;
    height: 100%;
    padding: 32px 16px;
    background-color: #fff;
    flex-shrink: 0;
}

.logo-section {
    margin-bottom: 60px;
}

.nav-menu {
    display: flex;
    flex-direction: column;
    gap: 16px;
    width: 100%;
    flex: 1;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 18px 24px;
    width: 100%;
    border-radius: 12px;
    font-size: 19px;
    color: #4a5568;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    user-select: none;
    caret-color: transparent;
}

.nav-item.active {
    border: 1px solid rgba(255, 86, 34, 0.2);
    background: rgba(255, 86, 34, 0.08);
    color: #ff5622;
    font-weight: 700;
    border-radius: 10px;
}

.nav-icon {
    width: 28px;
    height: 28px;
    stroke: currentColor;
    fill: none;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
}

.badge-container {
    display: flex;
    gap: 6px;
    margin-left: auto;
    width: fit-content;
}

.badge {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    font-size: 14px;
    font-weight: 600;
    color: #fff;
}

.badge.red {
    background: #ef4444;
}

.badge.yellow {
    background: #fbbf24;
    color: #000;
}

.settings-btn {
    display: flex;
    align-items: center;
    gap: 16px;
    width: 100%;
    padding: 18px 24px;
    margin-top: auto;
    border: 2px solid #e2e8f0;
    border-radius: 50px;
    background: #fff;
    font-size: 19px;
    color: #4a5568;
    cursor: pointer;
    transition: all 0.3s ease;
    user-select: none;
    caret-color: transparent;
}

.settings-icon {
    width: 24px;
    height: 24px;
}

.nav-item:focus,
.nav-item:focus-visible,
.settings-btn:focus,
.settings-btn:focus-visible {
    outline: none;
}

.nav-item *,
.settings-btn * {
    user-select: none;
    caret-color: transparent;
}
</style>
