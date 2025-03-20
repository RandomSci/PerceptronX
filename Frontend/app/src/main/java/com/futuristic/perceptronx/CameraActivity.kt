package com.futuristic.perceptronx

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.futuristic.perceptronx.ui.theme.PerceptronXTheme

class CameraActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            PerceptronXTheme {
                ActivateCamera()
            }
        }
    }
}
