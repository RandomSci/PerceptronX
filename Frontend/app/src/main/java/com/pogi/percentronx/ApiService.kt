package com.pogi.percentronx

import com.google.gson.annotations.SerializedName
import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

data class Login(
    val username: String,
    val password: String,
    val remember_me: Boolean = false
)

data class Register(
    val username: String,
    val email: String,
    val password: String
)

data class Status(
    val status: String
)

data class ErrorResponse(
    val detail: String
)

data class User_Data(
    val username: String,
    val email: String,
    val joined: String
)

data class Therapist(
    val id: Int,
    val name: String,
    val photoUrl: String,
    val specialties: List<String>,
    val bio: String,
    val experienceYears: Int,
    val education: List<String>,
    val languages: List<String>,
    val address: String,
    val rating: Float,
    val reviewCount: Int,
    val isAcceptingNewPatients: Boolean,
    val averageSessionLength: Int
)

data class TherapistListItem(
    val id: Int,
    val name: String,
    val photoUrl: String,
    val specialties: List<String>,
    val location: String,
    val rating: Float,
    val reviewCount: Int,
    val distance: Float,
    val nextAvailable: String
)

data class Review(
    val id: Int,
    val patientName: String,
    val rating: Float,
    val comment: String,
    val date: String
)

data class AvailableTimeSlot(
    val id: Int,
    val date: String,
    val time: String,
    val isAvailable: Boolean
)

data class AppointmentRequest(
    val therapist_id: Int,
    val date: String,
    val time: String,
    val type: String,
    val notes: String? = null,
    val insuranceProvider: String? = null,
    val insuranceMemberId: String? = null
)

data class AppointmentResponse(
    val status: String,
    val message: String
)

data class MessageRequest(
    val recipient_id: Int,
    val recipient_type: String = "therapist",
    val subject: String,
    val content: String
)

data class Patient(
    val id: Int,
    val name: String,
    val email: String,
    val phoneNumber: String,
    val profilePicture: String,
    val therapistId: Int
)

interface ApiService {

    @POST("loginUser")
    fun loginUser(@Body loginData: Login): Call<Status>

    @POST("registerUser")
    fun registerUser(@Body registerData: Register): Call<Status>

    @GET("/")
    suspend fun getStatus(): Status

    @POST("logout")
    fun logout(): Call<Status>

    @POST("reset-password")
    fun resetPassword(@Body email: Map<String, String>): Call<Status>

    @GET("getUserInfo")
    fun getUserInfo(): Call<User_Data>

    @GET("therapists")
    suspend fun getTherapists(): List<TherapistListItem>

    @GET("therapists/{id}")
    suspend fun getTherapistDetails(@Path("id") therapistId: Int): Therapist

    @POST("appointments/request")
    suspend fun requestAppointment(@Body request: AppointmentRequest): Status

    @GET("therapists/{id}/availability")
    suspend fun getTherapistAvailability(@Path("id") therapistId: Int): List<AvailableTimeSlot>

    @POST("messages/send")
    suspend fun sendMessage(@Body messageRequest: MessageRequest): Status

    @POST("therapists/{id}/add_patient")
    suspend fun addPatientToTherapist(
        @Path("id") therapistId: Int,
        @Body patient: Map<String, Any>
    ): Status

    @GET("user/appointments")
    suspend fun getUserAppointments(): List<Map<String, Any>>

    @GET("user/therapist")
    suspend fun getCurrentTherapist(): Therapist?

    @POST("therapists/{id}/rate")
    suspend fun rateTherapist(
        @Path("id") therapistId: Int,
        @Body rating: Map<String, Any>
    ): Status
}