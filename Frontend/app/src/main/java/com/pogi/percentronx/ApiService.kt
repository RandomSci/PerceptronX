package com.pogi.percentronx

import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

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
}