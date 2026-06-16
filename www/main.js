$(document).ready(function () {

    // --- MAGNETIC BUTTON EFFECT ---
    const magneticButtons = document.querySelectorAll('.btn-magnetic');
    magneticButtons.forEach(btn => {
        btn.addEventListener('mousemove', function(e) {
            const position = btn.getBoundingClientRect();
            const x = e.pageX - position.left - position.width / 2;
            const y = e.pageY - position.top - position.height / 2;
            btn.style.transform = `translate(${x * 0.3}px, ${y * 0.5}px)`;
        });
        btn.addEventListener('mouseout', function(e) {
            btn.style.transform = 'translate(0px, 0px)';
        });
    });

    $('.text').textillate({
        loop: true,
        sync: true,
        in: {
            effect: 'fadeInRight',
            sequence: true
        },
        out: {
            effect: 'bounceOut',
            sequence: true
        },
    });

    // Siri Wave Setup (Refined & Smaller)
    var siriWave = new SiriWave({
        container: document.getElementById("siri-container"),
        width: 600,
        height: 150,
        style: "ios9",
        amplitude: 2,
        speed: 0.1,
        autostart: true
    });

    // Siri wave animation text
    $('.siri-message').textillate({
        loop: true,
        sync: true,
        in: {
            effect: 'fadeInRight',
            sequence: true,
        },
        out: {
            effect: 'bounceOut',
            sequence: true
        },
    });

    // 🎤 Mic Button Event
    $("#MicBtn").click(function () {
        $("#oval").attr("hidden", true);
        $("#siriwave").attr("hidden", false);
        eel.allCommands(); // Voice parameter without passing string
    });

    // 💬 Send Button Event (Text Input)
    $("#SendBtn").click(function () {
        let textInput = $("#chatbox").val();
        if(textInput.trim() !== "") {
            // No need to show siriwave for typed input, let the backend decide (Chat or Home)
            eel.allCommands(textInput); 
            $("#chatbox").val("");
        }
    });

    // ⌨️ Enter Key Event for Chatbox
    $('#chatbox').keypress(function (e) {
        if (e.which == 13) {
            $("#SendBtn").click();
            return false;    
        }
    });

    // Back Button Event
    $("#BackBtn").click(function () {
        $("#chat-section").attr("hidden", true);
        $("#oval").attr("hidden", false);
    });

    // Inner Chat Input Logic
    $("#InnerSendBtn").click(function () {
        let textInput = $("#inner-chatbox").val();
        if(textInput.trim() !== "") {
            eel.allCommands(textInput); 
            $("#inner-chatbox").val("");
            // Scroll to bottom is handled in controller
        }
    });

    $('#inner-chatbox').keypress(function (e) {
        if (e.which == 13) {
            $("#InnerSendBtn").click();
            return false;    
        }
    });

    // Clear All History Logic
    $("#ClearHistoryBtn").click(async function() {
        if(confirm("Are you sure you want to clear all history?")) {
            await eel.ClearAllChats()();
            eel.RefreshChatHistory()();
            $("#chat-body").empty();
        }
    });

    // --- ADVANCED SETTINGS LOGIC ---
    function updateCoreSettings() {
        let personality = $("#aiPersonality").val();
        let language = $("#aiLanguage").val();
        let detail = $("#aiDetail").val();
        let voiceId = $("#voiceChanger").val();
        let isMuted = $("#voiceMute").is(":checked");
        
        eel.UpdateCoreSettings(personality, detail, isMuted, voiceId, language)();
    }

    $("#aiPersonality, #aiLanguage, #aiDetail, #voiceChanger, #voiceMute").change(function() {
        updateCoreSettings();
    });

    $("#ExportHistoryBtn").click(async function() {
        let textData = await eel.ExportChatHistory()();
        if(textData) {
            let blob = new Blob([textData], { type: "text/plain;charset=utf-8" });
            let url = window.URL.createObjectURL(blob);
            let a = document.createElement("a");
            a.href = url;
            a.download = "HeyBuddy_Chat_History.txt";
            a.click();
            window.URL.revokeObjectURL(url);
        }
    });

    $("#ResetAppBtn").click(function() {
        if(confirm("This will reload the application. Are you sure?")) {
            location.reload();
        }
    });

    // Siri Mic Toggle Logic
    $("#SiriMicBtn").click(function() {
        if ($(this).hasClass("mic-listening")) {
            $(this).removeClass("mic-listening");
            $(".siri-message").text("Paused... Click to Resume");
        } else {
            $(this).addClass("mic-listening");
            $(".siri-message").text("Listening...");
            eel.allCommands()(); 
        }
    });

    // Siri Back Button Logic
    $("#SiriBackBtn").click(function() {
        $("#siriwave").attr("hidden", true);
        $("#oval").attr("hidden", false);
    });

});