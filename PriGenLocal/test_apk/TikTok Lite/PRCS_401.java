/*Application Package Name: com.tiktok.lite.go
class PRCS_401 {
/**
X.442;L()I
*/

    public static int L()
    {
        try {
            android.accounts.Account[] v5_0;
            android.accounts.AccountManager v9 = android.accounts.AccountManager.get(X.16B.LB);
            com.bytedance.helios.statichook.api.HeliosApiHook v4_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            Object[] v10 = new Object[1];
            v10[0] = "com.google";
            com.bytedance.helios.statichook.api.ExtraInfo v11_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Ljava/lang/String;)[Landroid/accounts/Account;", "dzBzEhEpEcvSUUUuTBbKc9NnF3kueWo2KOurYJDb0ibECfF1owsk1PEpiJoiBqigUjzpYAGFnEDsIO0pLZdA");
            com.bytedance.helios.statichook.api.Result v1_0 = v4_1.preInvoke(102501, "android/accounts/AccountManager", "getAccountsByType", v9, v10, "android.accounts.Account[]", v11_1);
        } catch (Exception) {
            return -1;
        }
        if (!v1_0.intercept) {
            v5_0 = v9.getAccountsByType("com.google");
            v4_1.postInvoke(v5_0, 102501, "android/accounts/AccountManager", "getAccountsByType", v9, v10, v11_1, 1);
        } else {
            v4_1.postInvoke(0, 102501, "android/accounts/AccountManager", "getAccountsByType", v9, v10, v11_1, 0);
            v5_0 = ((android.accounts.Account[]) v1_0.returnValue);
        }
        return v5_0.length;
    }

/**
X.43u;invoke()Ljava/lang/Object;
*/

    public final synthetic Object invoke()
    {
        X.4DB v4_1 = new X.4DB();
        long v2_1 = new java.util.HashMap();
        v2_1.putAll(X.3tV.L());
        X.44k.L(this.L, this.LB, v4_1);
        X.44k.L(v4_1, v2_1);
        v4_1.L("enter_method", this.LB.LII());
        v4_1.L("enter_from", this.LB.LI());
        v4_1.L("enter_type", this.LB.LIIII());
        v4_1.L("is_register", this.LBL);
        v4_1.L("error_code", this.LC);
        v4_1.L("platform", this.LCC);
        v4_1.L("gms_auto_fill", this.LCCII);
        v4_1.L("login_total_time", (System.currentTimeMillis() - X.44k.L));
        v4_1.L("google_account_counts", X.442.L());
        X.4br.L("login_failure", v4_1.L);
        return Integer.valueOf(0);
    }


}