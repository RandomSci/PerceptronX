package com.pogi.percentronx

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.width
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

@Composable
fun register() {
    Box(
        modifier = Modifier.fillMaxSize()
            .height(30.dp)
            .width(30.dp)
            .background(Color(0xFF8FBFE6))
    ){
        Text(
            text = "Sign up test",
            color = Color.Black
        )
    }
}