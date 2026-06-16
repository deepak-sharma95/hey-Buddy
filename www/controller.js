$(document).ready(function () {



    // Display Speak Message
    eel.expose(DisplayMessage)
    function DisplayMessage(message) {
        // Replace the hidden textillate <li>
        $(".siri-message").text(message);
    }

    // Display hood (Assistant ki default screen wapas dikhaye aur wave chupaye)
    eel.expose(ShowHood)
    function ShowHood() {
        $("#oval").attr("hidden", false);
        $("#siriwave").attr("hidden", true);
    }

    // Show Chat Section
    eel.expose(ShowChatSection)
    function ShowChatSection() {
        $("#oval").attr("hidden", true);
        $("#siriwave").attr("hidden", true);
        $("#chat-section").attr("hidden", false);
    }

    // Add Message to Chat
    eel.expose(AddChatMessage)
    function AddChatMessage(senderType, message) {
        // senderType: 'sender' (user) or 'receiver' (bot)
        // message ko markdown format me ya text format me display karein
        // abhi direct text append kar rahe hain
        let msgHtml = `<div class="message ${senderType}">${message}</div>`;
        $("#chat-body").append(msgHtml);
        
        let chatBody = document.getElementById("chat-body");
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    // Show Typing Indicator
    eel.expose(ShowTypingIndicator)
    function ShowTypingIndicator() {
        let typingHtml = `<div class="typing-indicator" id="typing-indicator"><span></span><span></span><span></span></div>`;
        $("#chat-body").append(typingHtml);
        let chatBody = document.getElementById("chat-body");
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    // Remove Typing Indicator
    eel.expose(RemoveTypingIndicator)
    function RemoveTypingIndicator() {
        $("#typing-indicator").remove();
    }

    // Chat History Management
    eel.expose(RefreshChatHistory)
    function RefreshChatHistory() {
        LoadHistory();
    }

    async function LoadHistory() {
        let history = await eel.GetChatHistory()();
        $("#history-list").empty();
        if(history.length === 0) {
            $("#history-list").append("<p class='text-secondary text-center mt-3'>No history.</p>");
        }
        history.forEach(item => {
            // Encode quotes properly for inline onclick handlers
            // encodeURIComponent does not encode single quotes, so we manually encode them to %27
            let safeQuery = encodeURIComponent(item.query || "").replace(/'/g, "%27");
            let safeResponse = encodeURIComponent(item.response || "").replace(/'/g, "%27");
            
            let li = `<li class="history-item" onclick="openHistoryItem('${safeQuery}', '${safeResponse}')">
                        <p><i class="bi bi-chat-left-text me-2"></i> ${item.query}</p>
                        <button class="delete-history-btn" onclick="event.stopPropagation(); deleteHistoryItem(${item.id})"><i class="bi bi-trash"></i></button>
                      </li>`;
            $("#history-list").append(li);
        });
    }

    // Call initially
    LoadHistory();

    window.deleteHistoryItem = async function(id) {
        await eel.DeleteChat(id)();
        LoadHistory();
    };

    window.openHistoryItem = function(encodedQuery, encodedResponse) {
        let query = decodeURIComponent(encodedQuery);
        let response = decodeURIComponent(encodedResponse);
        
        $("#chat-body").empty(); // clear current window
        AddChatMessage("sender", query);
        AddChatMessage("receiver", response);
        
        // Close Offcanvas using Bootstrap
        let offcanvasEl = document.getElementById('historyOffcanvas');
        let bsOffcanvas = bootstrap.Offcanvas.getInstance(offcanvasEl);
        if (bsOffcanvas) {
            bsOffcanvas.hide();
        }
        
        // Ensure chat section is visible
        $("#oval").attr("hidden", true);
        $("#siriwave").attr("hidden", true);
        $("#chat-section").attr("hidden", false);
    };

});