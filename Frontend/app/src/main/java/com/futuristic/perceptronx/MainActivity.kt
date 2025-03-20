package com.futuristic.perceptronx

import android.Manifest
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.MediaStore
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import coil.compose.rememberAsyncImagePainter
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.outlined.History
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import com.futuristic.perceptronx.ui.theme.PerceptronXTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            PerceptronXTheme {
                PerceptronXHomeScreen()
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PerceptronXHomeScreen() {
    var realTimeDetectionEnabled by remember { mutableStateOf(false) }
    // Use a list for multiple selections; default selection is "All Objects"
    var selectedDetectionOptions by remember { mutableStateOf(listOf("All Objects")) }
    var expandedDetectionDropdown by remember { mutableStateOf(false) }
    var currentTab by remember { mutableStateOf(0) }
    var showCameraDialog by remember { mutableStateOf(false) }
    var showImagePickerDialog by remember { mutableStateOf(false) }
    var selectedImageUri by remember { mutableStateOf<Uri?>(null) }

    val context = LocalContext.current

    // Launcher for camera permission
    val cameraPermissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            // Launch the Camera screen
            val intent = Intent(context, CameraActivity::class.java)
            context.startActivity(intent)
        }
        showCameraDialog = false
    }

    // Image picker launcher
    val imagePickerLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let {
            // Store the selected image URI
            selectedImageUri = it

            // Launch the ImageAnalysisActivity
            val intent = Intent(context, ImageAnalysisActivity::class.java).apply {
                putExtra("IMAGE_URI", uri.toString())
            }
            context.startActivity(intent)
        }
        showImagePickerDialog = false
    }

    // Full list of detection classes available (YOLOv8)
    val detectionOptions = listOf(
        "All Objects", "People", "Vehicles", "Animals",
        "Bicycles", "Buses", "Cars", "Motorcycles", "Traffic Lights", "Stop Signs", "Trucks"
    )

    val darkBackground = Color(0xFF121212)
    val neonBlue = Color(0xFF00FFFF)
    val neonGreen = Color(0xFF39FF14)
    val darkGray = Color(0xFF1E1E1E)

    val backgroundGradient = Brush.verticalGradient(
        colors = listOf(
            darkBackground,
            Color(0xFF191919),
            Color(0xFF151515)
        )
    )

    // Camera permission dialog
    if (showCameraDialog) {
        AlertDialog(
            onDismissRequest = { showCameraDialog = false },
            title = { Text(text = "Camera Access") },
            text = { Text(text = "PerceptronX needs camera access for real-time object detection.") },
            confirmButton = {
                Button(
                    onClick = {
                        cameraPermissionLauncher.launch(Manifest.permission.CAMERA)
                    }
                ) {
                    Text(text = "Grant Access")
                }
            },
            dismissButton = {
                Button(onClick = { showCameraDialog = false }) {
                    Text(text = "Cancel")
                }
            }
        )
    }

    // Image picker dialog
    if (showImagePickerDialog) {
        AlertDialog(
            onDismissRequest = { showImagePickerDialog = false },
            title = { Text(text = "Upload Image") },
            text = { Text(text = "Select an image from your gallery for object detection analysis.") },
            confirmButton = {
                Button(
                    onClick = {
                        // Launch the image picker
                        imagePickerLauncher.launch("image/*")
                    }
                ) {
                    Text(text = "Select Image")
                }
            },
            dismissButton = {
                Button(onClick = { showImagePickerDialog = false }) {
                    Text(text = "Cancel")
                }
            }
        )
    }

    Scaffold(
        containerColor = Color.Transparent,
        bottomBar = {
            NavigationBar(
                containerColor = darkGray,
                contentColor = Color.White
            ) {
                NavigationBarItem(
                    selected = currentTab == 0,
                    onClick = { currentTab = 0 },
                    icon = { Icon(Icons.Filled.Home, contentDescription = "Home") },
                    label = { Text(text = "Home") }
                )
                NavigationBarItem(
                    selected = currentTab == 1,
                    onClick = { currentTab = 1 },
                    icon = { Icon(Icons.Outlined.History, contentDescription = "History") },
                    label = { Text(text = "History") }
                )
                NavigationBarItem(
                    selected = currentTab == 2,
                    onClick = { currentTab = 2 },
                    icon = { Icon(Icons.Filled.Settings, contentDescription = "Settings") },
                    label = { Text(text = "Settings") }
                )
                NavigationBarItem(
                    selected = currentTab == 3,
                    onClick = { currentTab = 3 },
                    icon = { Icon(Icons.Filled.Person, contentDescription = "Profile") },
                    label = { Text(text = "Profile") }
                )
            }
        }
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(brush = backgroundGradient)
                .padding(innerPadding)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(
                        brush = Brush.radialGradient(
                            colors = listOf(
                                Color(0x10004444),
                                Color(0x05002222)
                            )
                        )
                    )
            )
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Spacer(modifier = Modifier.height(32.dp))
                Text(
                    text = "PerceptronX",
                    color = Color.White,
                    fontSize = 40.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 2.sp
                )
                Text(
                    text = "AI-Powered Object Detection at Your Fingertips",
                    color = Color.LightGray,
                    fontSize = 16.sp,
                    letterSpacing = 0.5.sp,
                    modifier = Modifier.padding(top = 8.dp, bottom = 48.dp)
                )

                // Multi-select Detection Options Dropdown
                ExposedDropdownMenuBox(
                    expanded = expandedDetectionDropdown,
                    onExpandedChange = { expandedDetectionDropdown = !expandedDetectionDropdown }
                ) {
                    // Display selected options as comma-separated text
                    val displayText = if (selectedDetectionOptions.isEmpty()) {
                        "None"
                    } else {
                        selectedDetectionOptions.joinToString(", ")
                    }
                    OutlinedTextField(
                        value = displayText,
                        onValueChange = {},
                        readOnly = true,
                        label = { Text(text = "Objects to Detect") },
                        trailingIcon = {
                            ExposedDropdownMenuDefaults.TrailingIcon(expanded = expandedDetectionDropdown)
                        },
                        textStyle = TextStyle(color = Color.White),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedContainerColor = Color(0x30FFFFFF),
                            unfocusedContainerColor = Color(0x30FFFFFF),
                            disabledContainerColor = Color(0x30FFFFFF),
                            focusedBorderColor = neonBlue,
                            unfocusedBorderColor = Color(0x50FFFFFF)
                        ),
                        modifier = Modifier
                            .menuAnchor()
                            .fillMaxWidth()
                    )
                    ExposedDropdownMenu(
                        expanded = expandedDetectionDropdown,
                        onDismissRequest = { expandedDetectionDropdown = false }
                    ) {
                        detectionOptions.forEach { option ->
                            // Check if the option is selected
                            val isSelected = selectedDetectionOptions.contains(option)
                            DropdownMenuItem(
                                text = {
                                    Row(
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Checkbox(checked = isSelected, onCheckedChange = {
                                            // Toggle selection
                                            selectedDetectionOptions = if (isSelected) {
                                                selectedDetectionOptions - option
                                            } else {
                                                selectedDetectionOptions + option
                                            }
                                        })
                                        Spacer(modifier = Modifier.width(8.dp))
                                        Text(text = option)
                                    }
                                },
                                onClick = {
                                    // Allow tapping on the row to toggle the selection
                                    selectedDetectionOptions = if (isSelected) {
                                        selectedDetectionOptions - option
                                    } else {
                                        selectedDetectionOptions + option
                                    }
                                }
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(24.dp))
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = "Real-time Detection",
                        color = Color.White,
                        fontSize = 16.sp
                    )
                    Switch(
                        checked = realTimeDetectionEnabled,
                        onCheckedChange = { realTimeDetectionEnabled = it },
                        colors = SwitchDefaults.colors(
                            checkedThumbColor = Color.White,
                            checkedTrackColor = neonGreen,
                            uncheckedThumbColor = Color.White,
                            uncheckedTrackColor = Color.DarkGray
                        )
                    )
                }
                // Mode indicator
                Text(
                    text = if (realTimeDetectionEnabled)
                        "Mode: Camera Detection"
                    else
                        "Mode: Image Upload Analysis",
                    color = if (realTimeDetectionEnabled) neonGreen else neonBlue,
                    fontSize = 14.sp,
                    modifier = Modifier.padding(top = 8.dp)
                )
                Spacer(modifier = Modifier.weight(1f))
                // Start Detection Button
                Button(
                    onClick = {
                        if (realTimeDetectionEnabled) {
                            showCameraDialog = true
                        } else {
                            showImagePickerDialog = true
                        }
                    },
                    modifier = Modifier
                        .height(64.dp)
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(32.dp))
                        .background(
                            brush = Brush.horizontalGradient(
                                colors = listOf(neonBlue, neonGreen)
                            )
                        ),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color.Transparent
                    )
                ) {
                    Text(
                        text = if (realTimeDetectionEnabled)
                            "START CAMERA DETECTION"
                        else
                            "UPLOAD IMAGE FOR DETECTION",
                        color = Color.Black,
                        fontWeight = FontWeight.Bold,
                        fontSize = 16.sp,
                        letterSpacing = 1.sp
                    )
                }
                Spacer(modifier = Modifier.height(32.dp))
            }
        }
    }
}

@Preview(showBackground = true)
@Composable
fun PerceptronXHomeScreenPreview() {
    PerceptronXTheme {
        PerceptronXHomeScreen()
    }
}