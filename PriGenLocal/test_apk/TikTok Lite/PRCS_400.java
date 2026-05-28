/*Application Package Name: com.tiktok.lite.go
class PRCS_400 {
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
X.43w;invoke()Ljava/lang/Object;
*/

    public final synthetic Object invoke()
    {
        X.4DB v2_1 = new X.4DB();
        java.util.Map v1_5 = new java.util.HashMap();
        v1_5.putAll(X.3tV.L());
        X.44k.L(v2_1, v1_5);
        v2_1.L("enter_method", this.L.LII());
        v2_1.L("enter_from", this.L.LI());
        v2_1.L("enter_type", this.L.LIIII());
        v2_1.L("platform", this.LB);
        v2_1.L("log_pb", X.40N.L(this.L.LIIIL()));
        Integer v0_9 = this.LBL;
        if (v0_9 != null) {
            v2_1.L("is_register", v0_9.booleanValue());
        }
        if (this.LC) {
            v2_1.L("login_from", "reset_password");
        }
        X.44k.L(this.LCC, this.L, v2_1);
        v2_1.L("gms_auto_fill", this.LCCII);
        v2_1.L("google_account_counts", X.442.L());
        v2_1.L("is_skipable_login", this.LCI);
        X.4br.L("login_submit", v2_1.L);
        return Integer.valueOf(0);
    }


}