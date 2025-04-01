package com.pogi.percentronx

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.pogi.percentronx.ui.theme.PercentronXTheme
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            PercentronXTheme {
                val annotations = remember { mutableStateOf<List<AnnotationItem>>(emptyList()) }

                val errorMessage = remember { mutableStateOf<String?>(null) }

                LaunchedEffect(Unit) { fetchAnnotations(annotations, errorMessage) }

                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
                        Text("PerceptronX Annotations", style = MaterialTheme.typography.headlineMedium)
                        Spacer(modifier = Modifier.height(10.dp))

                        errorMessage.value?.let {
                            Card(
                                modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer)
                            ) {
                                Text(
                                    text = it,
                                    modifier = Modifier.padding(16.dp),
                                    color = MaterialTheme.colorScheme.onErrorContainer
                                )
                            }
                            Spacer(modifier = Modifier.height(10.dp))
                        }

                        if (annotations.value.isEmpty() && errorMessage.value == null) {
                            CircularProgressIndicator(
                                modifier = Modifier.align(androidx.compose.ui.Alignment.CenterHorizontally)
                            )
                        } else {
                            AnnotationList(annotations.value)
                        }
                    }
                }
            }
        }
    }

    private fun fetchAnnotations(
        annotations: MutableState<List<AnnotationItem>>,
        errorMessage: MutableState<String?>
    ) {
        retrofitClient.instance.getAnnotations().enqueue(object : Callback<AnnotationResponse> {
            override fun onResponse(call: Call<AnnotationResponse>, response: Response<AnnotationResponse>) {
                if (response.isSuccessful) {
                    val annotationResponse = response.body()
                    if (annotationResponse?.annotations != null) {
                        annotations.value = annotationResponse.annotations
                    } else if (annotationResponse?.message != null) {
                        errorMessage.value = annotationResponse.message
                    } else {
                        errorMessage.value = "Received empty response from server"
                    }
                } else {
                    errorMessage.value = "Error: ${response.code()} - ${response.message()}"
                }
            }

            override fun onFailure(call: Call<AnnotationResponse>, t: Throwable) {
                errorMessage.value = "Network Error: ${t.message}"
            }
        })
    }
}

@Composable
fun AnnotationList(items: List<AnnotationItem>) {
    LazyColumn {
        items(items) { annotation ->
            Card(
                modifier = Modifier.fillMaxWidth().padding(8.dp),
                shape = MaterialTheme.shapes.medium,
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "ID: ${annotation._id}",
                        style = MaterialTheme.typography.titleMedium
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "Model: ${annotation.model_used}",
                        style = MaterialTheme.typography.bodyMedium
                    )
                    Text(
                        text = "Status: ${annotation.status}",
                        style = MaterialTheme.typography.bodyMedium
                    )
                    Text(
                        text = "Time: ${annotation.timestamp}",
                        style = MaterialTheme.typography.bodyMedium
                    )

                    Text(
                        text = "Annotations: ${annotation.annotations.size}",
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }
        }
    }
}