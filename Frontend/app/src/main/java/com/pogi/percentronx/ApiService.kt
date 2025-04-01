package com.pogi.percentronx

import retrofit2.Call
import retrofit2.http.GET

data class AnnotationResponse(
    val annotations: List<AnnotationItem>? = null,
    val message: String? = null
)

data class AnnotationItem(
    val id: String,
    val user_id: String,
    val image: String,
    val annotations: List<AnnotationDetail>,
    val size: ImageSize,
    val save_location: String,
    val model_used: String,
    val timestamp: String,
    val status: String,
    val confidence_threshold: Double,
    val processing_time: Double,
    val device: String
) {
    val _id: String get() = id
}

data class AnnotationDetail(
    val `class`: String,
    val confidence: Double,
    val bbox: List<Int>
)

data class ImageSize(
    val height: Int,
    val width: Int
)

interface ApiService {
    @GET("/")
    fun getAnnotations(): Call<AnnotationResponse>



}