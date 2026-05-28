/*Application Package Name: org.fdroid.fdroid
class PRCS_26 {
/**
androidx.work.impl.utils.NetworkApi24;m(Landroid/net/ConnectivityManager; Landroid/net/ConnectivityManager$NetworkCallback;)V
*/

    public static bridge synthetic void m(android.net.ConnectivityManager p0, android.net.ConnectivityManager$NetworkCallback p1)
    {
        p0.registerDefaultNetworkCallback(p1);
        return;
    }

/**
androidx.work.impl.utils.NetworkApi24;registerDefaultNetworkCallbackCompat(Landroid/net/ConnectivityManager; Landroid/net/ConnectivityManager$NetworkCallback;)V
*/

    public static final void registerDefaultNetworkCallbackCompat(android.net.ConnectivityManager p1, android.net.ConnectivityManager$NetworkCallback p2)
    {
        kotlin.jvm.internal.Intrinsics.checkNotNullParameter(p1, "<this>");
        kotlin.jvm.internal.Intrinsics.checkNotNullParameter(p2, "networkCallback");
        androidx.work.impl.utils.NetworkApi24$$ExternalSyntheticApiModelOutline0.m(p1, p2);
        return;
    }

/**
androidx.work.impl.constraints.trackers.NetworkStateTracker24;startTracking()V
*/

    public void startTracking()
    {
        try {
            androidx.work.Logger.get().debug(androidx.work.impl.constraints.trackers.NetworkStateTrackerKt.access$getTAG$p(), "Registering network callback");
            androidx.work.impl.utils.NetworkApi24.registerDefaultNetworkCallbackCompat(this.connectivityManager, this.networkCallback);
        } catch (SecurityException v1_1) {
            androidx.work.Logger.get().error(androidx.work.impl.constraints.trackers.NetworkStateTrackerKt.access$getTAG$p(), "Received exception while registering network callback", v1_1);
        } catch (SecurityException v1_0) {
            androidx.work.Logger.get().error(androidx.work.impl.constraints.trackers.NetworkStateTrackerKt.access$getTAG$p(), "Received exception while registering network callback", v1_0);
        }
        return;
    }


}