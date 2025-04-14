package com.pogi.percentronx

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.Create
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Divider
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import coil.compose.rememberAsyncImagePainter
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TherapistDetailsScreen(
    navController: NavController,
    therapistId: Int
) {
    val coroutineScope = rememberCoroutineScope()
    var therapist by remember { mutableStateOf<Therapist?>(null) }
    var isLoading by remember { mutableStateOf(true) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    var selectedTabIndex by remember { mutableIntStateOf(0) }

    val tabs = listOf("Overview", "Availability", "Reviews")
    LaunchedEffect(key1 = therapistId) {
        try {
            isLoading = true
            val result = retrofitClient.instance.getTherapistDetails(therapistId)
            therapist = result
            isLoading = false
        } catch (e: Exception) {
            isLoading = false
            errorMessage = "Error loading therapist details: ${e.message}"
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(therapist?.name ?: "Therapist Details") },
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
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            if (isLoading) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            } else if (errorMessage != null) {
                Box(
                    modifier = Modifier.fillMaxSize(),
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
            } else {
                therapist?.let { theTherapist ->
                    Column(
                        modifier = Modifier.fillMaxSize()
                    ) {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .background(MaterialTheme.colorScheme.primaryContainer)
                                .padding(16.dp)
                        ) {
                            Column(
                                horizontalAlignment = Alignment.CenterHorizontally,
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(120.dp)
                                        .clip(CircleShape)
                                        .background(MaterialTheme.colorScheme.background)
                                ) {
                                    Image(
                                        painter = rememberAsyncImagePainter(
                                            model = theTherapist.photoUrl.ifEmpty { "https://via.placeholder.com/120" }
                                        ),
                                        contentDescription = "Therapist photo",
                                        modifier = Modifier.fillMaxSize(),
                                        contentScale = ContentScale.Crop
                                    )
                                }

                                Spacer(modifier = Modifier.height(16.dp))

                                Text(
                                    text = theTherapist.name,
                                    style = MaterialTheme.typography.headlineSmall,
                                    fontWeight = FontWeight.Bold,
                                    color = MaterialTheme.colorScheme.onPrimaryContainer
                                )

                                Spacer(modifier = Modifier.height(4.dp))

                                Text(
                                    text = theTherapist.specialties.joinToString(", "),
                                    style = MaterialTheme.typography.bodyMedium,
                                    color = MaterialTheme.colorScheme.onPrimaryContainer,
                                    textAlign = TextAlign.Center
                                )

                                Spacer(modifier = Modifier.height(8.dp))

                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.Center
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.Star,
                                        contentDescription = "Rating",
                                        tint = Color(0xFFFFC107),
                                        modifier = Modifier.size(20.dp)
                                    )
                                    Spacer(modifier = Modifier.width(4.dp))
                                    Text(
                                        text = "${theTherapist.rating}",
                                        style = MaterialTheme.typography.bodyMedium,
                                        color = MaterialTheme.colorScheme.onPrimaryContainer
                                    )

                                    Spacer(modifier = Modifier.width(4.dp))

                                    Text(
                                        text = "(${theTherapist.reviewCount} reviews)",
                                        style = MaterialTheme.typography.bodyMedium,
                                        color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
                                    )
                                }
                            }
                        }
                        TabRow(
                            selectedTabIndex = selectedTabIndex
                        ) {
                            tabs.forEachIndexed { index, title ->
                                Tab(
                                    selected = selectedTabIndex == index,
                                    onClick = { selectedTabIndex = index },
                                    text = { Text(title) }
                                )
                            }
                        }
                        when (selectedTabIndex) {
                            0 -> TherapistOverviewTab(theTherapist)
                            1 -> TherapistAvailabilityTab(therapistId, navController)
                            2 -> TherapistReviewsTab(therapistId)
                        }
                        Box(
                            modifier = Modifier
                                .fillMaxSize()
                                .padding(16.dp),
                            contentAlignment = Alignment.BottomEnd
                        ) {
                            FloatingActionButton(
                                onClick = {
                                    navController.navigate("therapist_chat/${therapistId}")
                                }
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Email,
                                    contentDescription = "Chat with therapist"
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun TherapistOverviewTab(therapist: Therapist) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp)
    ) {
        Text(
            text = "About",
            style = MaterialTheme.typography.titleLarge,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = therapist.bio,
            style = MaterialTheme.typography.bodyMedium
        )

        Spacer(modifier = Modifier.height(16.dp))
        InfoRow(
            icon = Icons.Default.Build,
            title = "Experience",
            value = "${therapist.experienceYears} years"
        )

        Spacer(modifier = Modifier.height(8.dp))
        InfoRow(
            icon = Icons.Default.Info,
            title = "Education",
            infoList = therapist.education
        )

        Spacer(modifier = Modifier.height(8.dp))
        InfoRow(
            icon = Icons.Default.Create,
            title = "Languages",
            infoList = therapist.languages
        )

        Spacer(modifier = Modifier.height(8.dp))
        InfoRow(
            icon = Icons.Default.LocationOn,
            title = "Address",
            value = therapist.address
        )

        Spacer(modifier = Modifier.height(8.dp))
        InfoRow(
            icon = Icons.Default.Notifications,
            title = "Average Session Length",
            value = "${therapist.averageSessionLength} minutes"
        )

        Spacer(modifier = Modifier.height(24.dp))
    }
}

@Composable
fun InfoRow(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    title: String,
    value: String? = null,
    infoList: List<String>? = null
) {
    Row(
        verticalAlignment = Alignment.Top,
        modifier = Modifier.fillMaxWidth()
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier.size(24.dp)
        )

        Spacer(modifier = Modifier.width(16.dp))

        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(4.dp))

            if (!value.isNullOrEmpty()) {
                Text(
                    text = value,
                    style = MaterialTheme.typography.bodyMedium
                )
            } else if (!infoList.isNullOrEmpty()) {
                Column {
                    infoList.forEach { item ->
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.padding(vertical = 2.dp)
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(6.dp)
                                    .clip(CircleShape)
                                    .background(MaterialTheme.colorScheme.primary)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = item,
                                style = MaterialTheme.typography.bodyMedium
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun TherapistAvailabilityTab(therapistId: Int, navController: NavController) {
    var availableTimeSlots by remember { mutableStateOf<List<AvailableTimeSlot>>(emptyList()) }
    var isLoading by remember { mutableStateOf(true) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    val coroutineScope = rememberCoroutineScope()

    LaunchedEffect(key1 = therapistId) {
        try {
            isLoading = true
            val result = retrofitClient.instance.getTherapistAvailability(therapistId)
            availableTimeSlots = result
            isLoading = false
        } catch (e: Exception) {
            isLoading = false
            errorMessage = "Error loading availability: ${e.message}"
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        if (isLoading) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else if (errorMessage != null) {
            Box(
                modifier = Modifier.fillMaxSize(),
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
                                val result = retrofitClient.instance.getTherapistAvailability(therapistId)
                                availableTimeSlots = result
                                isLoading = false
                            } catch (e: Exception) {
                                isLoading = false
                                errorMessage = "Error loading availability: ${e.message}"
                            }
                        }
                    }) {
                        Text("Retry")
                    }
                }
            }
        } else if (availableTimeSlots.isEmpty()) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(
                        imageVector = Icons.Default.DateRange,
                        contentDescription = "No Availability",
                        tint = MaterialTheme.colorScheme.primary.copy(alpha = 0.5f),
                        modifier = Modifier.size(48.dp)
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "No available time slots found",
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)
                    )
                    Spacer(modifier = Modifier.height(24.dp))
                    Button(
                        onClick = { navController.navigate("request_appointment/$therapistId") }
                    ) {
                        Text("Request Custom Appointment")
                    }
                }
            }
        } else {
            Text(
                text = "Available Time Slots",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(16.dp))
            val groupedSlots = availableTimeSlots.groupBy { it.date }

            LazyColumn {
                groupedSlots.forEach { (date, slots) ->
                    item {
                        Text(
                            text = date,
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(vertical = 8.dp)
                        )

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            slots.forEach { slot ->
                                TimeSlotChip(
                                    timeSlot = slot,
                                    onClick = {
                                        if (slot.isAvailable) {
                                            navController.navigate("book_appointment/$therapistId/${slot.id}")
                                        }
                                    }
                                )
                            }
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            Button(
                onClick = { navController.navigate("request_appointment/$therapistId") },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Request Custom Appointment")
            }
        }
    }
}

@Composable
fun TimeSlotChip(
    timeSlot: AvailableTimeSlot,
    onClick: () -> Unit
) {
    Surface(
        modifier = Modifier
            .padding(4.dp),
        shape = RoundedCornerShape(16.dp),
        color = if (timeSlot.isAvailable)
            MaterialTheme.colorScheme.primary
        else
            MaterialTheme.colorScheme.surfaceVariant,
        enabled = timeSlot.isAvailable,
        onClick = onClick
    ) {
        Text(
            text = timeSlot.time,
            style = MaterialTheme.typography.bodyMedium,
            color = if (timeSlot.isAvailable)
                MaterialTheme.colorScheme.onPrimary
            else
                MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.6f),
            modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
        )
    }
}

@Composable
fun TherapistReviewsTab(therapistId: Int) {
    var reviews by remember { mutableStateOf<List<Review>>(emptyList()) }
    var isLoading by remember { mutableStateOf(true) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(key1 = therapistId) {
        try {
            isLoading = true

            val mockReviews = listOf(
                Review(
                    id = 1,
                    patientName = "Example review 1",
                    rating = 5.0f,
                    comment = "Example COMMENT 1",
                    date = "2023-05-15"
                ),
                Review(
                    id = 2,
                    patientName = "Example review 2",
                    rating = 4.5f,
                    comment = "Example COMMENT 1",
                    date = "2023-04-22"
                ),
                Review(
                    id = 3,
                    patientName = "Example 3",
                    rating = 5.0f,
                    comment = "Example COMMENT 1",
                    date = "2023-03-10"
                )
            )
            reviews = mockReviews
            isLoading = false
        } catch (e: Exception) {
            isLoading = false
            errorMessage = "Error loading reviews: ${e.message}"
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        if (isLoading) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else if (errorMessage != null) {
            Box(
                modifier = Modifier.fillMaxSize(),
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
                }
            }
        } else if (reviews.isEmpty()) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(
                        imageVector = Icons.Default.Star,
                        contentDescription = "No Reviews",
                        tint = MaterialTheme.colorScheme.primary.copy(alpha = 0.5f),
                        modifier = Modifier.size(48.dp)
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "No reviews yet",
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)
                    )
                }
            }
        } else {
            Text(
                text = "Patient Reviews",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(16.dp))

            LazyColumn {
                items(reviews) { review ->
                    ReviewItem(review)
                    Divider(
                        modifier = Modifier.padding(vertical = 16.dp),
                        color = MaterialTheme.colorScheme.outlineVariant
                    )
                }
            }
        }
    }
}

@Composable
fun ReviewItem(review: Review) {
    Column {
        Row(
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = review.patientName,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.weight(1f))

            val dateFormatter = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
            val formattedDate = try {
                val date = dateFormatter.parse(review.date)
                SimpleDateFormat("MMM dd, yyyy", Locale.getDefault()).format(date!!)
            } catch (e: Exception) {
                review.date
            }

            Text(
                text = formattedDate,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
            )
        }

        Spacer(modifier = Modifier.height(4.dp))

        Row(verticalAlignment = Alignment.CenterVertically) {
            for (i in 1..5) {
                Icon(
                    imageVector = Icons.Default.Star,
                    contentDescription = null,
                    tint = if (i <= review.rating) Color(0xFFFFC107) else Color.LightGray,
                    modifier = Modifier.size(16.dp)
                )
                Spacer(modifier = Modifier.width(2.dp))
            }

            Spacer(modifier = Modifier.width(8.dp))

            Text(
                text = review.rating.toString(),
                style = MaterialTheme.typography.bodyMedium
            )
        }

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = review.comment,
            style = MaterialTheme.typography.bodyMedium
        )
    }
}