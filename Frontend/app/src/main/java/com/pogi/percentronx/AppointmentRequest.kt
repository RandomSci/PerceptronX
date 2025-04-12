package com.pogi.percentronx

import android.widget.Toast
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RequestAppointmentScreen(
    navController: NavController,
    therapistId: Int
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()

    // State variables
    var therapist by remember { mutableStateOf<Therapist?>(null) }
    var isLoading by remember { mutableStateOf(true) }
    var isSubmitting by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    // Form fields
    var selectedDate by remember { mutableStateOf("") }
    var selectedTime by remember { mutableStateOf("") }
    var appointmentType by remember { mutableStateOf("Initial Consultation") }
    var notes by remember { mutableStateOf("") }
    var insuranceProvider by remember { mutableStateOf("") }
    var insuranceMemberId by remember { mutableStateOf("") }
    var showDatePicker by remember { mutableStateOf(false) }
    var showTimePicker by remember { mutableStateOf(false) }

    // Date picker state
    val datePickerState = rememberDatePickerState(
        initialSelectedDateMillis = System.currentTimeMillis()
    )

    // Appointment types
    val appointmentTypes = listOf(
        "Initial Consultation",
        "Regular Session",
        "Follow-up",
        "Emergency Session"
    )

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

    // Date picker dialog
    if (showDatePicker) {
        DatePickerDialog(
            onDismissRequest = { showDatePicker = false },
            confirmButton = {
                TextButton(
                    onClick = {
                        datePickerState.selectedDateMillis?.let { dateMillis ->
                            val date = Date(dateMillis)
                            val sdf = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
                            selectedDate = sdf.format(date)
                        }
                        showDatePicker = false
                    }
                ) {
                    Text("Confirm")
                }
            },
            dismissButton = {
                TextButton(onClick = { showDatePicker = false }) {
                    Text("Cancel")
                }
            }
        ) {
            DatePicker(state = datePickerState)
        }
    }

    // Time picker dialog (simplified version, would use a proper time picker in a real app)
    if (showTimePicker) {
        AlertDialog(
            onDismissRequest = { showTimePicker = false },
            title = { Text("Select Time") },
            text = {
                Column {
                    val timeSlots = listOf(
                        "09:00 AM", "10:00 AM", "11:00 AM",
                        "01:00 PM", "02:00 PM", "03:00 PM", "04:00 PM"
                    )
                    timeSlots.forEach { time ->
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 4.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            RadioButton(
                                selected = selectedTime == time,
                                onClick = { selectedTime = time }
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(time)
                        }
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = { showTimePicker = false }) {
                    Text("Confirm")
                }
            },
            dismissButton = {
                TextButton(onClick = { showTimePicker = false }) {
                    Text("Cancel")
                }
            }
        )
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Request Appointment") },
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
                .padding(16.dp)
                .verticalScroll(rememberScrollState())
        ) {
            if (isLoading) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            } else {
                therapist?.let { theTherapist ->
                    Text(
                        text = "Request Appointment with ${theTherapist.name}",
                        style = MaterialTheme.typography.titleLarge
                    )

                    Spacer(modifier = Modifier.height(24.dp))

                    // Date selection
                    OutlinedTextField(
                        value = selectedDate,
                        onValueChange = { },
                        readOnly = true,
                        label = { Text("Preferred Date") },
                        placeholder = { Text("Select Date") },
                        trailingIcon = {
                            IconButton(onClick = { showDatePicker = true }) {
                                Icon(
                                    imageVector = Icons.Default.DateRange,
                                    contentDescription = "Select Date"
                                )
                            }
                        },
                        modifier = Modifier.fillMaxWidth()
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    // Time selection
                    OutlinedTextField(
                        value = selectedTime,
                        onValueChange = { },
                        readOnly = true,
                        label = { Text("Preferred Time") },
                        placeholder = { Text("Select Time") },
                        trailingIcon = {
                            IconButton(onClick = { showTimePicker = true }) {
                                Icon(
                                    imageVector = Icons.Default.Star,
                                    contentDescription = "Select Time"
                                )
                            }
                        },
                        modifier = Modifier.fillMaxWidth()
                    )

                    Spacer(modifier = Modifier.height(16.dp))

                    // Appointment type selection
                    var appointmentTypeExpanded by remember { mutableStateOf(false) }

                    ExposedDropdownMenuBox(
                        expanded = appointmentTypeExpanded,
                        onExpandedChange = { appointmentTypeExpanded = it }
                    ) {
                        OutlinedTextField(
                            value = appointmentType,
                            onValueChange = {},
                            readOnly = true,
                            label = { Text("Appointment Type") },
                            trailingIcon = {
                                ExposedDropdownMenuDefaults.TrailingIcon(expanded = appointmentTypeExpanded)
                            },
                            modifier = Modifier
                                .fillMaxWidth()
                                .menuAnchor()
                        )

                        ExposedDropdownMenu(
                            expanded = appointmentTypeExpanded,
                            onDismissRequest = { appointmentTypeExpanded = false }
                        ) {
                            appointmentTypes.forEach { type ->
                                DropdownMenuItem(
                                    text = { Text(type) },
                                    onClick = {
                                        appointmentType = type
                                        appointmentTypeExpanded = false
                                    }
                                )
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    // Notes field
                    OutlinedTextField(
                        value = notes,
                        onValueChange = { notes = it },
                        label = { Text("Notes (optional)") },
                        placeholder = { Text("Any specific concerns or information for the therapist") },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(120.dp),
                        minLines = 3
                    )

                    Spacer(modifier = Modifier.height(24.dp))

                    // Insurance information section
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(16.dp)
                        ) {
                            Text(
                                text = "Insurance Information (Optional)",
                                style = MaterialTheme.typography.titleMedium
                            )

                            Spacer(modifier = Modifier.height(16.dp))

                            OutlinedTextField(
                                value = insuranceProvider,
                                onValueChange = { insuranceProvider = it },
                                label = { Text("Insurance Provider") },
                                placeholder = { Text("e.g. Blue Cross, Aetna") },
                                modifier = Modifier.fillMaxWidth()
                            )

                            Spacer(modifier = Modifier.height(16.dp))

                            OutlinedTextField(
                                value = insuranceMemberId,
                                onValueChange = { insuranceMemberId = it },
                                label = { Text("Member ID / Policy Number") },
                                modifier = Modifier.fillMaxWidth(),
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(24.dp))

                    // Error message
                    if (errorMessage != null) {
                        Text(
                            text = errorMessage ?: "",
                            color = MaterialTheme.colorScheme.error,
                            modifier = Modifier.padding(vertical = 8.dp)
                        )
                    }

                    // Submit button
                    Button(
                        onClick = {
                            if (selectedDate.isBlank()) {
                                errorMessage = "Please select a preferred date"
                                return@Button
                            }

                            if (selectedTime.isBlank()) {
                                errorMessage = "Please select a preferred time"
                                return@Button
                            }

                            // Clear previous error
                            errorMessage = null
                            isSubmitting = true

                            // Create appointment request
                            val appointmentRequest = AppointmentRequest(
                                therapistId = therapistId,
                                date = selectedDate,
                                time = selectedTime,
                                type = appointmentType,
                                notes = notes.ifBlank { null },
                                insuranceProvider = insuranceProvider.ifBlank { null },
                                insuranceMemberId = insuranceMemberId.ifBlank { null }
                            )

                            // Submit request
                            coroutineScope.launch {
                                try {
                                    val response = retrofitClient.instance.requestAppointment(appointmentRequest)
                                    isSubmitting = false

                                    if (response.status == "success") {
                                        Toast.makeText(
                                            context,
                                            "Appointment request sent successfully!",
                                            Toast.LENGTH_LONG
                                        ).show()
                                        navController.navigate("dashboard") {
                                            popUpTo("dashboard") { inclusive = true }
                                        }
                                    } else {
                                        errorMessage = "Failed to request appointment. Please try again."
                                    }
                                } catch (e: Exception) {
                                    isSubmitting = false
                                    errorMessage = "Error: ${e.message}"
                                }
                            }
                        },
                        modifier = Modifier.fillMaxWidth(),
                        enabled = !isSubmitting
                    ) {
                        if (isSubmitting) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(24.dp),
                                color = MaterialTheme.colorScheme.onPrimary,
                                strokeWidth = 2.dp
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                        }
                        Text("Submit Request")
                    }
                }
            }
        }
    }
}