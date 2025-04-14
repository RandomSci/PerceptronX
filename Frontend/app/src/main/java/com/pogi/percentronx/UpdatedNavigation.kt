package com.pogi.percentronx

import android.util.Log
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.ExperimentalAnimationApi
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInHorizontally
import androidx.compose.animation.slideOutHorizontally
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavController
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument

@Composable
fun UpdatedNavigationGraph() {
    val navController = rememberNavController()
    var status by remember { mutableStateOf<String?>(null) }
    var isLoading by remember { mutableStateOf(true) }
    var hasTherapist by remember { mutableStateOf(false) }

    LaunchedEffect(key1 = Unit) {
        try {
            val response = retrofitClient.instance.getStatus()
            status = response.status
            Log.d("API", "Status received: $status")
        } catch (e: Exception) {
            status = "invalid"
            Log.e("API", "Failure: ${e.message}")
        } finally {
            isLoading = false
        }
    }

    if (isLoading) {
        LoadingScreen()
    } else {
        Scaffold(
            bottomBar = {
                val currentRoute = navController.currentBackStackEntryAsState().value?.destination?.route
                val showBottomBar = currentRoute in bottomNavItems.map { it.route }

                if (showBottomBar) {
                    BottomNavigationBar(navController)
                }
            }
        ) { innerPadding ->
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding)
            ) {
                NavHost(
                    navController = navController,
                    startDestination = if (status == "valid") "main" else "profile"
                ) {
                    composable(
                        "main",
                        enterTransition = {
                            slideInHorizontally(initialOffsetX = { -it }) + fadeIn()
                        },
                        exitTransition = {
                            slideOutHorizontally(targetOffsetX = { -it }) + fadeOut()
                        }
                    ) {
                        MainScreen()
                    }

                    composable(
                        "dashboard",
                        enterTransition = {
                            slideInHorizontally(initialOffsetX = { it }) + fadeIn()
                        },
                        exitTransition = {
                            slideOutHorizontally(targetOffsetX = { it }) + fadeOut()
                        }
                    ) {
                        UpdatedDashboard(
                            navController = navController,
                            hasTherapist = hasTherapist,
                            isLoggedIn = status == "valid"
                        )
                    }

                    composable(
                        "activity",
                        enterTransition = {
                            slideInHorizontally(initialOffsetX = { it }) + fadeIn()
                        },
                        exitTransition = {
                            slideOutHorizontally(targetOffsetX = { it }) + fadeOut()
                        }
                    ) {
                        Activity()
                    }

                    composable("profile") {
                        Profile(
                            initialStatus = status,  // Pass the current status to avoid unnecessary API calls
                            onAuthStateChanged = { newStatus ->
                                status = newStatus
                                if (newStatus == "valid") {
                                    navController.navigate("main") {
                                        popUpTo(navController.graph.findStartDestination().id) {
                                            saveState = true
                                        }
                                        launchSingleTop = true
                                        restoreState = true
                                    }
                                }
                            }
                        )
                    }
                    composable("therapist_finder") {
                        TherapistFinderScreen(navController)
                    }

                    composable(
                        "therapist_details/{therapistId}",
                        arguments = listOf(
                            navArgument("therapistId") { type = NavType.IntType }
                        )
                    ) { backStackEntry ->
                        val therapistId = backStackEntry.arguments?.getInt("therapistId") ?: 0
                        TherapistDetailsScreen(navController, therapistId)
                    }

                    composable(
                        "request_appointment/{therapistId}",
                        arguments = listOf(
                            navArgument("therapistId") { type = NavType.IntType }
                        )
                    ) { backStackEntry ->
                        val therapistId = backStackEntry.arguments?.getInt("therapistId") ?: 0
                        RequestAppointmentScreen(navController, therapistId)
                    }

                    composable(
                        "book_appointment/{therapistId}/{slotId}",
                        arguments = listOf(
                            navArgument("therapistId") { type = NavType.IntType },
                            navArgument("slotId") { type = NavType.IntType }
                        )
                    ) { backStackEntry ->
                        val therapistId = backStackEntry.arguments?.getInt("therapistId") ?: 0
                        val slotId = backStackEntry.arguments?.getInt("slotId") ?: 0
                        RequestAppointmentScreen(navController, therapistId)
                    }

                    composable(
                        "therapist_chat/{therapistId}",
                        arguments = listOf(
                            navArgument("therapistId") { type = NavType.IntType }
                        )
                    ) { backStackEntry ->
                        val therapistId = backStackEntry.arguments?.getInt("therapistId") ?: 0
                        TherapistChatScreen(navController, therapistId)
                    }
                }
            }
        }
    }
}