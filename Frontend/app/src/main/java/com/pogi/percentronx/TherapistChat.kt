package com.pogi.percentronx

import android.widget.Toast
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.material.icons.filled.Done
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.Send
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.material3.TextFieldDefaults
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import coil.compose.rememberAsyncImagePainter
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Date
import java.util.Locale

data class ChatMessage(
    val id: Int,
    val senderId: Int,
    val receiverId: Int,
    val senderType: String, // "user" or "therapist"
    val content: String,
    val timestamp: Date,
    val isRead: Boolean
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TherapistChatScreen(
    navController: NavController,
    therapistId: Int
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val focusManager = LocalFocusManager.current
    val focusRequester = remember { FocusRequester() }

    var therapist by remember { mutableStateOf<Therapist?>(null) }
    var isLoading by remember { mutableStateOf(true) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    var messageText by remember { mutableStateOf("") }
    var isSending by remember { mutableStateOf(false) }

    // Mock messages for demo purposes
    var messages by remember { mutableStateOf<List<ChatMessage>>(emptyList()) }
    val scrollState = rememberLazyListState()

    // Define sendMessage function here at the top level of the composable
    val sendMessage: () -> Unit = sendMessage@{
        if (messageText.isBlank() || isSending) return@sendMessage

        val content = messageText.trim()
        messageText = ""
        isSending = true
        focusManager.clearFocus()

        coroutineScope.launch {
            try {
                // For a real app, you would create and use a message request like this:
                // val messageRequest = MessageRequest(
                //     recipient_id = therapistId,
                //     recipient_type = "therapist",
                //     subject = "Chat Message",
                //     content = content
                // )

                // In a real app, this would send to the server
                // For demo purposes, we'll just add it to our local message list
                val newMessage = ChatMessage(
                    id = (messages.maxOfOrNull { it.id } ?: 0) + 1,
                    senderId = 1, // User ID
                    receiverId = therapistId,
                    senderType = "user",
                    content = content,
                    timestamp = Calendar.getInstance().time,
                    isRead = false
                )

                messages = messages + newMessage

                // Simulate API call
                delay(500)

                try {
                    // This would be the actual API call in a real app
                    // val response = retrofitClient.instance.sendMessage(messageRequest)

                    // Simulate a response from the therapist after a delay
                    delay(2000)
                    if (content.contains("hello", ignoreCase = true) ||
                        content.contains("hi", ignoreCase = true)) {
                        val responseMessage = ChatMessage(
                            id = (messages.maxOfOrNull { it.id } ?: 0) + 1,
                            senderId = therapistId,
                            receiverId = 1, // User ID
                            senderType = "therapist",
                            content = "Hello! How can I help you today?",
                            timestamp = Calendar.getInstance().time,
                            isRead = true
                        )
                        messages = messages + responseMessage
                    } else if (content.contains("appointment", ignoreCase = true) ||
                        content.contains("schedule", ignoreCase = true)) {
                        val responseMessage = ChatMessage(
                            id = (messages.maxOfOrNull { it.id } ?: 0) + 1,
                            senderId = therapistId,
                            receiverId = 1, // User ID
                            senderType = "therapist",
                            content = "I'd be happy to schedule an appointment with you. Would you prefer to use the appointment scheduling feature, or would you like me to suggest some available times?",
                            timestamp = Calendar.getInstance().time,
                            isRead = true
                        )
                        messages = messages + responseMessage
                    } else {
                        val responseMessage = ChatMessage(
                            id = (messages.maxOfOrNull { it.id } ?: 0) + 1,
                            senderId = therapistId,
                            receiverId = 1, // User ID
                            senderType = "therapist",
                            content = "Thank you for your message. I'll get back to you as soon as possible.",
                            timestamp = Calendar.getInstance().time,
                            isRead = true
                        )
                        messages = messages + responseMessage
                    }

                } catch (e: Exception) {
                    Toast.makeText(
                        context,
                        "Failed to send message: ${e.message}",
                        Toast.LENGTH_SHORT
                    ).show()
                }

                isSending = false

            } catch (e: Exception) {
                isSending = false
                Toast.makeText(
                    context,
                    "Error: ${e.message}",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }
    }

    // Load therapist details
    LaunchedEffect(key1 = therapistId) {
        try {
            isLoading = true
            val result = retrofitClient.instance.getTherapistDetails(therapistId)
            therapist = result

            // Mock messages for UI demo
            val mockMessages = mutableListOf<ChatMessage>()
            val formatter = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())

            // Simulate a conversation
            mockMessages.add(
                ChatMessage(
                    id = 1,
                    senderId = 1, // User ID
                    receiverId = therapistId,
                    senderType = "user",
                    content = "Hello, I've been feeling anxious lately and would like to schedule a session.",
                    timestamp = formatter.parse("2023-06-10 10:30:00")!!,
                    isRead = true
                )
            )

            mockMessages.add(
                ChatMessage(
                    id = 2,
                    senderId = therapistId,
                    receiverId = 1, // User ID
                    senderType = "therapist",
                    content = "Hello! I'm sorry to hear you're feeling anxious. I'd be happy to help. I have some availability next week. Would you prefer morning or afternoon sessions?",
                    timestamp = formatter.parse("2023-06-10 11:15:00")!!,
                    isRead = true
                )
            )

            mockMessages.add(
                ChatMessage(
                    id = 3,
                    senderId = 1, // User ID
                    receiverId = therapistId,
                    senderType = "user",
                    content = "Afternoons would work better for me. I'm available on Tuesday or Thursday.",
                    timestamp = formatter.parse("2023-06-10 12:05:00")!!,
                    isRead = true
                )
            )

            mockMessages.add(
                ChatMessage(
                    id = 4,
                    senderId = therapistId,
                    receiverId = 1, // User ID
                    senderType = "therapist",
                    content = "Great! I can schedule you for Tuesday at 2:00 PM. Does that work for you?",
                    timestamp = formatter.parse("2023-06-10 13:30:00")!!,
                    isRead = true
                )
            )

            mockMessages.add(
                ChatMessage(
                    id = 5,
                    senderId = 1, // User ID
                    receiverId = therapistId,
                    senderType = "user",
                    content = "Tuesday at 2:00 PM works perfectly for me. Thank you!",
                    timestamp = formatter.parse("2023-06-10 14:15:00")!!,
                    isRead = true
                )
            )

            mockMessages.add(
                ChatMessage(
                    id = 6,
                    senderId = therapistId,
                    receiverId = 1, // User ID
                    senderType = "therapist",
                    content = "Excellent! I've scheduled you for Tuesday at 2:00 PM. Looking forward to our session. If you need anything before then, feel free to message me here.",
                    timestamp = formatter.parse("2023-06-10 14:45:00")!!,
                    isRead = true
                )
            )

            messages = mockMessages
            isLoading = false

            // Scroll to bottom of chat
            delay(300) // Small delay to ensure layout is complete
            scrollState.animateScrollToItem(messages.size - 1)
        } catch (e: Exception) {
            isLoading = false
            errorMessage = "Error loading therapist details: ${e.message}"
        }
    }

    // Auto-scroll to bottom when new messages are added
    LaunchedEffect(messages.size) {
        if (messages.isNotEmpty()) {
            scrollState.animateScrollToItem(messages.size - 1)
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        therapist?.let { theTherapist ->
                            Box(
                                modifier = Modifier
                                    .size(40.dp)
                                    .clip(CircleShape)
                                    .background(MaterialTheme.colorScheme.primaryContainer)
                            ) {
                                Image(
                                    painter = rememberAsyncImagePainter(
                                        model = theTherapist.photoUrl.ifEmpty { "https://via.placeholder.com/40" }
                                    ),
                                    contentDescription = "Therapist photo",
                                    modifier = Modifier.fillMaxSize(),
                                    contentScale = ContentScale.Crop
                                )
                            }

                            Spacer(modifier = Modifier.width(12.dp))

                            Column {
                                Text(
                                    text = theTherapist.name,
                                    style = MaterialTheme.typography.titleMedium
                                )
                                Text(
                                    text = if (messages.isNotEmpty()) "Online" else "Offline",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = if (messages.isNotEmpty())
                                        Color(0xFF4CAF50)
                                    else
                                        Color.Gray
                                )
                            }
                        } ?: run {
                            Text("Chat")
                        }
                    }
                },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(
                            imageVector = Icons.Default.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                }
            )
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            Column(modifier = Modifier.fillMaxSize()) {
                if (isLoading) {
                    Box(
                        modifier = Modifier.weight(1f),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator()
                    }
                } else if (errorMessage != null) {
                    Box(
                        modifier = Modifier.weight(1f),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Icon(
                                imageVector = Icons.Default.Warning,
                                contentDescription = "Error",
                                tint = MaterialTheme.colorScheme.error,
                                modifier = Modifier.size(48.dp)
                            )
                            Spacer(modifier = Modifier.height(16.dp))
                            Text(
                                text = errorMessage ?: "An unknown error occurred",
                                color = MaterialTheme.colorScheme.error
                            )
                            Spacer(modifier = Modifier.height(16.dp))
                            Button(onClick = {
                                coroutineScope.launch {
                                    errorMessage = null
                                    isLoading = true
                                    try {
                                        val result = retrofitClient.instance.getTherapistDetails(therapistId)
                                        therapist = result
                                        isLoading = false
                                    } catch (e: Exception) {
                                        isLoading = false
                                        errorMessage = "Error loading therapist details: ${e.message}"
                                    }
                                }
                            }) {
                                Text("Retry")
                            }
                        }
                    }
                } else if (messages.isEmpty()) {
                    Box(
                        modifier = Modifier.weight(1f),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Icon(
                                imageVector = Icons.Default.Email,
                                contentDescription = "No Messages",
                                tint = MaterialTheme.colorScheme.primary.copy(alpha = 0.5f),
                                modifier = Modifier.size(48.dp)
                            )
                            Spacer(modifier = Modifier.height(16.dp))
                            Text(
                                text = "No messages yet. Start the conversation!",
                                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)
                            )
                        }
                    }
                } else {
                    // Chat messages
                    LazyColumn(
                        modifier = Modifier
                            .weight(1f)
                            .fillMaxWidth()
                            .padding(horizontal = 16.dp),
                        state = scrollState,
                        contentPadding = PaddingValues(vertical = 16.dp)
                    ) {
                        items(messages) { message ->
                            ChatMessageItem(
                                message = message,
                                isFromUser = message.senderType == "user"
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                        }
                    }
                }

                // Message input
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    shape = RoundedCornerShape(24.dp),
                    elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        TextField(
                            value = messageText,
                            onValueChange = { messageText = it },
                            placeholder = { Text("Type a message...") },
                            modifier = Modifier
                                .weight(1f)
                                .focusRequester(focusRequester),
                            colors = TextFieldDefaults.colors(
                                focusedContainerColor = Color.Transparent,
                                unfocusedContainerColor = Color.Transparent,
                                disabledContainerColor = Color.Transparent,
                                focusedIndicatorColor = Color.Transparent,
                                unfocusedIndicatorColor = Color.Transparent,
                            ),
                            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                            keyboardActions = KeyboardActions(
                                onSend = {
                                    if (messageText.isNotBlank() && !isSending) {
                                        sendMessage()
                                    }
                                }
                            ),
                            maxLines = 4
                        )

                        IconButton(
                            onClick = {
                                if (messageText.isNotBlank() && !isSending) {
                                    sendMessage()
                                }
                            },
                            enabled = messageText.isNotBlank() && !isSending
                        ) {
                            Icon(
                                imageVector = Icons.Default.Send,
                                contentDescription = "Send",
                                tint = MaterialTheme.colorScheme.primary
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun ChatMessageItem(
    message: ChatMessage,
    isFromUser: Boolean
) {
    val dateFormatter = SimpleDateFormat("h:mm a", Locale.getDefault())
    val formattedTime = dateFormatter.format(message.timestamp)

    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = if (isFromUser) Alignment.End else Alignment.Start
    ) {
        Box(
            modifier = Modifier
                .widthIn(max = 280.dp)
                .clip(
                    RoundedCornerShape(
                        topStart = 16.dp,
                        topEnd = 16.dp,
                        bottomStart = if (isFromUser) 16.dp else 4.dp,
                        bottomEnd = if (isFromUser) 4.dp else 16.dp
                    )
                )
                .background(
                    if (isFromUser)
                        MaterialTheme.colorScheme.primary
                    else
                        MaterialTheme.colorScheme.surfaceVariant
                )
                .padding(12.dp)
        ) {
            Text(
                text = message.content,
                color = if (isFromUser)
                    MaterialTheme.colorScheme.onPrimary
                else
                    MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        Spacer(modifier = Modifier.height(4.dp))

        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = if (isFromUser) Arrangement.End else Arrangement.Start,
            modifier = Modifier.padding(horizontal = 4.dp)
        ) {
            Text(
                text = formattedTime,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.6f)
            )

            if (isFromUser) {
                Spacer(modifier = Modifier.width(4.dp))
                Icon(
                    imageVector = if (message.isRead) Icons.Default.Done else Icons.Default.DateRange,
                    contentDescription = if (message.isRead) "Read" else "Sent",
                    tint = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.6f),
                    modifier = Modifier.size(16.dp)
                )
            }
        }
    }
}
