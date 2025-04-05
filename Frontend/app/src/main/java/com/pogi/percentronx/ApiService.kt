package com.pogi.percentronx

import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

data class Status(val status: String)
data class Login(val username: String, val password: String)
data class Register(val username: String, val email: String, val password: String)

interface ApiService {
    @GET("/")
    fun getStatus(): Call<Status>

    @POST("/registerUser")
    fun registerUser(@Body request: Register):
            Call<Status>

    @POST("/loginUser")
    fun loginUser(@Body request: Login):
            Call<Status>
}