package com.futuristic.perceptronx

import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.rememberAsyncImagePainter
import com.futuristic.perceptronx.ui.theme.PerceptronXTheme

class ImageAnalysisActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val imageUriString = intent.getStringExtra("IMAGE_URI")
        val imageUri = if (imageUriString != null) Uri.parse(imageUriString) else null

        setContent {
            PerceptronXTheme {
                ImageAnalysisScreen(imageUri)
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ImageAnalysisScreen(imageUri: Uri?) {
    val darkBackground = Color(0xFF121212)
    val neonBlue = Color(0xFF00FFFF)
    val neonGreen = Color(0xFF39FF14)

    var isAnalyzing by remember { mutableStateOf(true) }
    var detectedObjects by remember { mutableStateOf(listOf<String>()) }

    // Simulate detection process (replace with real ML detection)
    LaunchedEffect(imageUri) {
        // In a real app, this is where you'd run your ML model
        kotlinx.coroutines.delay(2000) // Simulate processing time
        detectedObjects = listOf("Person (98%)", "Chair (87%)", "Table (76%)")
        isAnalyzing = false
    }

    val backgroundGradient = Brush.verticalGradient(
        colors = listOf(
            darkBackground,
            Color(0xFF191919),
            Color(0xFF151515)
        )
    )

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(text = "Image Analysis", color = Color.White) },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = darkBackground
                )
            )
        },
        containerColor = Color.Transparent
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(brush = backgroundGradient)
                .padding(paddingValues)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Image preview
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(300.dp)
                        .padding(16.dp)
                ) {
                    if (imageUri != null) {
                        Image(
                            painter = rememberAsyncImagePainter(imageUri),
                            contentDescription = "Selected image",
                            modifier = Modifier.fillMaxSize()
                        )
                    } else {
                        Text(
                            text = "No image selected",
                            color = Color.White,
                            modifier = Modifier.align(Alignment.Center)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(24.dp))

                // Analysis results
                Text(
                    text = "Detection Results",
                    color = Color.White,
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold
                )

                Spacer(modifier = Modifier.height(16.dp))

                if (isAnalyzing) {
                    CircularProgressIndicator(
                        color = neonBlue,
                        modifier = Modifier.size(48.dp)
                    )
                    Text(
                        text = "Analyzing image...",
                        color = Color.White,
                        modifier = Modifier.padding(top = 16.dp)
                    )
                } else {
                    if (detectedObjects.isEmpty()) {
                        Text(
                            text = "No objects detected",
                            color = Color.White
                        )
                    } else {
                        Column(
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            detectedObjects.forEach { item ->
                                Card(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(vertical = 4.dp),
                                    colors = CardDefaults.cardColors(
                                        containerColor = Color(0x30FFFFFF)
                                    )
                                ) {
                                    Text(
                                        text = item,
                                        color = Color.White,
                                        modifier = Modifier.padding(16.dp)
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}